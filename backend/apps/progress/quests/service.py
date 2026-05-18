"""Quest service — generation, the event-driven progress counter, and
the read-side current-period state builder.

Phase 2: rows + counters only. There is deliberately NO XP / points
payout and NO claim transition here — claiming and rewards are Phase 3.

Period scoping: every read and write resolves "now" through
`periods.py` (which reuses the streak service's Europe/Bucharest
"today"). Nothing in this module ever touches an assignment from a
period other than the current daily / weekly one.
"""
import logging

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.users.models import StudentProfile

from .catalog import DAILY_MILESTONES, QUEST_CATALOG, daily_quests, weekly_quests
from .models import DailyChallengeProgress, QuestAssignment
from .periods import daily_period_key, today_local, weekly_period_key

logger = logging.getLogger(__name__)

# Catalog insertion order — the order quests are presented to the
# student. The DB Meta ordering is -created_at, which is not meaningful
# for display, so the state builder re-sorts by this.
_CATALOG_ORDER = {slug: i for i, slug in enumerate(QUEST_CATALOG)}


def _resolve_profile(user):
    """StudentProfile for `user`, or None for non-students.

    Mirrors the `award_xp` resolution so quest wiring degrades the same
    way XP wiring does when the caller isn't a student.
    """
    return StudentProfile.objects.filter(user=user).first()


# ── Generation ──────────────────────────────────────────────────────────────

def sync_quests(user) -> dict:
    """Idempotently ensure `user`'s current-period quest state, then
    return it.

    Ensures one QuestAssignment per daily catalog entry at today's
    daily period key, one per weekly entry at this week's weekly period
    key, and today's DailyChallengeProgress row. `target` is snapshotted
    from the catalog on create; a re-sync is a pure no-op (get_or_create
    leans on the (student, quest_slug, period_key) unique constraint, so
    a concurrent double-sync resolves to the same rows).

    Past-period assignments (relative to each cadence's current key)
    that were never claimed are bulk-marked `expired` so they fall out
    of the active set without lingering as stale "completed".

    The generic `login` event is emitted through the same counter every
    other event uses — but only on the day's first sync (the call that
    creates today's DailyChallengeProgress), so the weekly login quest
    counts distinct calendar days rather than sync calls.
    """
    profile = _resolve_profile(user)
    if profile is None:
        return _empty_state()

    today = today_local()
    daily_pk = daily_period_key(today)
    weekly_pk = weekly_period_key(today)

    # Expire this student's past-period, never-claimed assignments. A
    # bulk maintenance sweep — the only place sync deliberately reaches
    # outside the current period. Claimed rows are preserved as history.
    QuestAssignment.objects.filter(
        student=profile,
        status__in=[
            QuestAssignment.Status.ACTIVE,
            QuestAssignment.Status.COMPLETED,
        ],
    ).filter(
        (Q(cadence=QuestAssignment.Cadence.DAILY) & ~Q(period_key=daily_pk))
        | (Q(cadence=QuestAssignment.Cadence.WEEKLY) & ~Q(period_key=weekly_pk))
    ).update(status=QuestAssignment.Status.EXPIRED)

    for q in daily_quests():
        QuestAssignment.objects.get_or_create(
            student=profile,
            quest_slug=q.slug,
            period_key=daily_pk,
            defaults={
                "cadence": QuestAssignment.Cadence.DAILY,
                "target": q.target_count,
            },
        )
    for q in weekly_quests():
        QuestAssignment.objects.get_or_create(
            student=profile,
            quest_slug=q.slug,
            period_key=weekly_pk,
            defaults={
                "cadence": QuestAssignment.Cadence.WEEKLY,
                "target": q.target_count,
            },
        )
    _, bar_created = DailyChallengeProgress.objects.get_or_create(
        student=profile, date=today,
    )

    # Generic login emission, gated to the day's first sync (the call
    # that created today's bar row). This makes the weekly login quest
    # count distinct days, not sync calls. Defensive: ensuring the rows
    # is the primary mutation and must survive a counter failure.
    if bar_created:
        try:
            record_quest_progress(user, "login")
        except Exception:
            logger.warning("Quest login emission failed", exc_info=True)

    return build_current_period_state(user)


# ── Event-driven progress counter ───────────────────────────────────────────

def record_quest_progress(user, event: str, context: dict | None = None) -> None:
    """Advance the student's active current-period quests for `event`.

    Finds every active assignment in the current daily / weekly period
    whose catalog goal_type matches `event`, locks each row, and bumps
    `progress` by one (never past `target`). The bump that reaches the
    target flips the row to `completed` and stamps `completed_at`.

    `context` is unused this phase — accepted now so the Phase-2 wiring
    contract is stable when Phase 3 needs richer event payloads.

    Defensive contract (Block 10 cross-system hook): call sites lazy-
    import and wrap this so a counter bug can never roll back the
    caller's primary mutation. The DB work runs in its own atomic block
    so a failure here doesn't poison an enclosing transaction.
    """
    profile = _resolve_profile(user)
    if profile is None:
        return

    slugs = [
        slug for slug, q in QUEST_CATALOG.items() if q.goal_type == event
    ]
    if not slugs:
        return

    today = today_local()
    daily_pk = daily_period_key(today)
    weekly_pk = weekly_period_key(today)
    now = timezone.now()

    with transaction.atomic():
        assignments = (
            QuestAssignment.objects
            .select_for_update()
            .filter(
                student=profile,
                status=QuestAssignment.Status.ACTIVE,
                quest_slug__in=slugs,
            )
            .filter(
                Q(cadence=QuestAssignment.Cadence.DAILY, period_key=daily_pk)
                | Q(cadence=QuestAssignment.Cadence.WEEKLY, period_key=weekly_pk)
            )
        )
        for a in assignments:
            if a.progress >= a.target:
                continue
            a.progress = min(a.progress + 1, a.target)
            if a.progress >= a.target:
                a.status = QuestAssignment.Status.COMPLETED
                a.completed_at = now
                a.save(update_fields=["progress", "status", "completed_at"])
            else:
                a.save(update_fields=["progress"])


# ── Claim paths ─────────────────────────────────────────────────────────────

class QuestClaimError(Exception):
    """A claim was rejected. Carries the Romanian message and the HTTP
    status the view should surface."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


_MILESTONE_XP = {threshold: xp for (threshold, xp) in DAILY_MILESTONES}


def claim_quest(user, assignment_id: int) -> dict:
    """Claim a completed quest assignment: flip it to `claimed`, pay its
    catalog `xp_reward` into the student's current-grade pet, and (for a
    daily quest) accrue its `point_value` to today's points bar.

    Idempotency rests on the status check: only a `completed` →
    `claimed` transition is allowed, so a repeat call is rejected (and
    the assignment-id-scoped XP key is a second guard). Stale-period
    claims are refused — the assignment's period must still be current
    for its cadence.

    Returns {assignment, xp_gained, bar} where `bar` is the updated
    daily bar for a daily claim, else None. Raises QuestClaimError on
    any validation failure.
    """
    from apps.progress.xp import award_xp, student_grade  # Block 10 cycle

    profile = _resolve_profile(user)
    if profile is None:
        raise QuestClaimError("Doar elevii pot revendica misiuni.", 403)

    assignment = (
        QuestAssignment.objects
        .filter(pk=assignment_id, student=profile)
        .first()
    )
    if assignment is None:
        raise QuestClaimError("Misiunea nu există.", 404)

    today = today_local()
    current_pk = (
        daily_period_key(today)
        if assignment.cadence == QuestAssignment.Cadence.DAILY
        else weekly_period_key(today)
    )
    if assignment.period_key != current_pk:
        raise QuestClaimError(
            "Misiunea aparține unei perioade încheiate.", 400,
        )

    _reject_unclaimable(assignment.status)

    quest = QUEST_CATALOG.get(assignment.quest_slug)
    xp_reward = quest.xp_reward if quest else 0
    now = timezone.now()

    with transaction.atomic():
        locked = (
            QuestAssignment.objects.select_for_update().get(pk=assignment.pk)
        )
        # Re-check under the row lock (TOCTOU + the idempotency guard).
        _reject_unclaimable(locked.status)

        locked.status = QuestAssignment.Status.CLAIMED
        locked.claimed_at = now
        locked.save(update_fields=["status", "claimed_at"])

        grade = student_grade(user)
        xp_gained = 0
        if grade is not None and xp_reward:
            xp_gained = award_xp(
                user,
                "quest_completed",
                {"assignment_id": locked.pk, "xp": xp_reward},
                grade,
            )

        bar_data = None
        if locked.cadence == QuestAssignment.Cadence.DAILY:
            point_value = quest.point_value if quest else 0
            DailyChallengeProgress.objects.get_or_create(
                student=profile, date=today,
            )
            locked_bar = (
                DailyChallengeProgress.objects
                .select_for_update()
                .get(student=profile, date=today)
            )
            if point_value:
                locked_bar.points += point_value
                locked_bar.save(update_fields=["points"])
            bar_data = _serialize_bar(locked_bar, today)

    return {
        "assignment": _serialize_assignment(locked),
        "xp_gained": xp_gained,
        "bar": bar_data,
    }


def _reject_unclaimable(status: str) -> None:
    if status == QuestAssignment.Status.CLAIMED:
        raise QuestClaimError("Misiunea a fost deja revendicată.", 400)
    if status != QuestAssignment.Status.COMPLETED:
        raise QuestClaimError("Misiunea nu este finalizată.", 400)


def claim_milestone(user, threshold: int) -> dict:
    """Claim a daily points-bar milestone: record the threshold and pay
    its DAILY_MILESTONES XP into the student's current-grade pet.

    Idempotency rests on `claimed_thresholds` membership. Today's bar
    row must already exist (this never creates one) and hold enough
    points. Returns {bar, xp_gained}; raises QuestClaimError otherwise.
    """
    from apps.progress.xp import award_xp, student_grade  # Block 10 cycle

    profile = _resolve_profile(user)
    if profile is None:
        raise QuestClaimError("Doar elevii pot revendica recompense.", 403)

    if threshold not in _MILESTONE_XP:
        raise QuestClaimError("Prag invalid.", 400)

    today = today_local()
    bar = (
        DailyChallengeProgress.objects
        .filter(student=profile, date=today)
        .first()
    )
    if bar is None:
        raise QuestClaimError("Nu există progres pentru ziua de azi.", 400)
    _reject_milestone(bar.points, bar.claimed_thresholds, threshold)

    rung_xp = _MILESTONE_XP[threshold]

    with transaction.atomic():
        locked_bar = (
            DailyChallengeProgress.objects.select_for_update().get(pk=bar.pk)
        )
        # Re-check under the row lock (TOCTOU + the idempotency guard).
        _reject_milestone(
            locked_bar.points, locked_bar.claimed_thresholds, threshold,
        )

        claimed = list(locked_bar.claimed_thresholds)
        claimed.append(threshold)
        locked_bar.claimed_thresholds = claimed
        locked_bar.save(update_fields=["claimed_thresholds"])

        grade = student_grade(user)
        xp_gained = 0
        if grade is not None and rung_xp:
            xp_gained = award_xp(
                user,
                "daily_milestone",
                {
                    "date": today.isoformat(),
                    "threshold": threshold,
                    "xp": rung_xp,
                },
                grade,
            )

    return {
        "bar": _serialize_bar(locked_bar, today),
        "xp_gained": xp_gained,
    }


def _reject_milestone(points: int, claimed: list, threshold: int) -> None:
    if threshold in claimed:
        raise QuestClaimError("Pragul a fost deja revendicat.", 400)
    if points < threshold:
        raise QuestClaimError(
            "Nu ai suficiente puncte pentru acest prag.", 400,
        )


# ── Read-side state ─────────────────────────────────────────────────────────

def build_current_period_state(user) -> dict:
    """Read-only snapshot of `user`'s current-period quests + points bar.

    Bulk queries only (one for assignments, one for the bar), enriched
    in memory from the catalog — same shape/discipline as the other
    progress read views. Never creates rows: a student who has never
    synced today gets a zeroed bar derived from the catalog.
    """
    profile = _resolve_profile(user)
    if profile is None:
        return _empty_state()

    today = today_local()
    daily_pk = daily_period_key(today)
    weekly_pk = weekly_period_key(today)

    assignments = list(
        QuestAssignment.objects.filter(
            student=profile,
        ).filter(
            Q(cadence=QuestAssignment.Cadence.DAILY, period_key=daily_pk)
            | Q(cadence=QuestAssignment.Cadence.WEEKLY, period_key=weekly_pk)
        )
    )
    assignments.sort(key=lambda a: _CATALOG_ORDER.get(a.quest_slug, 1_000))

    daily = [
        _serialize_assignment(a)
        for a in assignments
        if a.cadence == QuestAssignment.Cadence.DAILY
    ]
    weekly = [
        _serialize_assignment(a)
        for a in assignments
        if a.cadence == QuestAssignment.Cadence.WEEKLY
    ]

    bar = (
        DailyChallengeProgress.objects
        .filter(student=profile, date=today)
        .first()
    )

    return {
        "daily_period_key": daily_pk,
        "weekly_period_key": weekly_pk,
        "daily": daily,
        "weekly": weekly,
        "bar": _serialize_bar(bar, today),
    }


def _serialize_assignment(a: QuestAssignment) -> dict:
    q = QUEST_CATALOG.get(a.quest_slug)
    return {
        "slug": a.quest_slug,
        "cadence": a.cadence,
        "goal_type": q.goal_type if q else None,
        "title": q.title if q else a.quest_slug,
        "description": q.description if q else "",
        "progress": a.progress,
        "target": a.target,
        "status": a.status,
        "xp_reward": q.xp_reward if q else None,
        "point_value": q.point_value if q else None,
        "period_key": a.period_key,
        "completed_at": a.completed_at.isoformat() if a.completed_at else None,
        "claimed_at": a.claimed_at.isoformat() if a.claimed_at else None,
    }


def _serialize_bar(bar: DailyChallengeProgress | None, today) -> dict:
    points = bar.points if bar else 0
    claimed = list(bar.claimed_thresholds) if bar else []
    return {
        "date": (bar.date if bar else today).isoformat(),
        "points": points,
        "claimed_thresholds": claimed,
        "milestones": [
            {"threshold": t, "xp_reward": xp, "claimed": t in claimed}
            for (t, xp) in DAILY_MILESTONES
        ],
    }


def _empty_state() -> dict:
    """State for a non-student caller — no rows, catalog-shaped bar."""
    today = today_local()
    return {
        "daily_period_key": daily_period_key(today),
        "weekly_period_key": weekly_period_key(today),
        "daily": [],
        "weekly": [],
        "bar": _serialize_bar(None, today),
    }
