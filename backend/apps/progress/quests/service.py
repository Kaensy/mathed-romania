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

    After the rows exist it emits the generic `login` event through the
    same counter every other event uses — so the login quest needs no
    special-casing here or anywhere else.
    """
    profile = _resolve_profile(user)
    if profile is None:
        return _empty_state()

    today = today_local()
    daily_pk = daily_period_key(today)
    weekly_pk = weekly_period_key(today)

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
    DailyChallengeProgress.objects.get_or_create(student=profile, date=today)

    # Generic login emission. Defensive: ensuring the rows is the
    # primary mutation and must survive a counter failure. NOTE: this
    # fires on every sync, so weekly_login effectively counts "synced
    # this week" rather than distinct calendar days — an accepted
    # Phase-2 simplification (no special-casing, per spec).
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
