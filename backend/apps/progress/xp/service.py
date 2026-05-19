"""XP service — `award_xp` is the single entry point for granting XP.

Idempotency is enforced at the database via the unique constraint on
(student, idempotency_key) in XPLedger; a duplicate grant raises
IntegrityError, which we catch and translate to a 0 return.

`total_xp` on StudentProfile and `pet_xp` on the per-grade Pet are both
maintained inside the same atomic block. We use `select_for_update +
save` (rather than F-expressions) so the pre/post values are available
to fire `pet_level_up` and `xp_milestone` badge events on the row's
transition. The row-level lock keeps concurrent grants linearizable —
each waits for the previous one to commit before reading the latest
value.
"""
import logging

from django.db import IntegrityError, transaction

from apps.content.models import Grade, Topic, Unit
from apps.pets.levels import level_for_xp
from apps.pets.models import Pet
from apps.users.models import StudentProfile

from .awards import XP_AWARDS
from .models import XPLedger

logger = logging.getLogger(__name__)

# Lifetime XP milestone bucket size. Crossing a multiple of this fires
# the `xp_milestone` badge event. Keep in sync with the milestone
# evaluators in apps.progress.badges.evaluators.
_XP_MILESTONE_BUCKET = 1000


def student_grade(user):
    """Resolve the `content.Grade` row for a student user.

    Returns None when the user is not a student or the StudentProfile's
    grade integer doesn't match any Grade row. Callers that need a
    `grade` argument for `award_xp` should treat None as "skip the award".
    """
    profile = StudentProfile.objects.filter(user=user).only("grade").first()
    if profile is None:
        return None
    return Grade.objects.filter(number=profile.grade).first()


def content_grade_for_topic(topic_id):
    """Resolve the `content.Grade` for a topic via topic → unit → grade.

    Content-based XP (lesson opens, category-tier clears, topic-test
    progression) routes to the *content's* grade ledger/pet, not the
    student's current grade — a Grade-7 student reviewing Grade-5
    content earns onto the Grade-5 pet. `total_xp` is unaffected; it
    accumulates every grant regardless of grade.

    Returns None for an unknown topic id (caller treats None as "skip").
    """
    topic = (
        Topic.objects
        .select_related("unit__grade")
        .filter(pk=topic_id)
        .first()
    )
    return topic.unit.grade if topic is not None else None


def content_grade_for_unit(unit_id):
    """Resolve the `content.Grade` for a unit via unit → grade.

    Companion to `content_grade_for_topic` for unit-scoped test XP.
    Returns None for an unknown unit id.
    """
    unit = Unit.objects.select_related("grade").filter(pk=unit_id).first()
    return unit.grade if unit is not None else None


def award_xp(user, source: str, context: dict, grade) -> int:
    """Grant XP for `source` to `user`, scoped by the source's
    key_builder(context).

    Returns the amount granted on success, or 0 if the user has no
    StudentProfile or the grant duplicates an existing ledger row.
    Raises KeyError if `source` is not in XP_AWARDS.
    """
    profile = StudentProfile.objects.filter(user=user).first()
    if profile is None:
        return 0

    if source not in XP_AWARDS:
        raise KeyError(f"Unknown XP source: {source!r}")

    award = XP_AWARDS[source]
    amount = award["amount"]
    if callable(amount):
        # Per-grant amount (quest/milestone payouts carry it in context).
        amount = amount(context)
    key = award["key_builder"](context)

    try:
        with transaction.atomic():
            XPLedger.objects.create(
                student=user,
                source=source,
                amount=amount,
                grade=grade,
                idempotency_key=key,
            )

            # ── total_xp on StudentProfile (locked, save pattern) ─────
            locked_profile = (
                StudentProfile.objects.select_for_update().get(pk=profile.pk)
            )
            old_total = locked_profile.total_xp
            new_total = old_total + amount
            locked_profile.total_xp = new_total
            locked_profile.save(update_fields=["total_xp"])

            # ── pet_xp on per-grade Pet (locked, save pattern) ────────
            # Skip silently when the student has no pet for this grade
            # (e.g., grade unmapped in pets.species).
            old_pet_level = None
            new_pet_level = None
            locked_pet = (
                Pet.objects.select_for_update()
                .filter(student=profile, grade=grade)
                .first()
            )
            if locked_pet is not None:
                old_pet_level = level_for_xp(locked_pet.pet_xp)
                locked_pet.pet_xp = locked_pet.pet_xp + amount
                locked_pet.save(update_fields=["pet_xp"])
                new_pet_level = level_for_xp(locked_pet.pet_xp)

            # ── Milestone badge events (still inside the transaction) ─
            # Pet level transitions: only fire on an actual level change.
            if (
                new_pet_level is not None
                and old_pet_level is not None
                and new_pet_level > old_pet_level
            ):
                _safe_evaluate_badges(
                    user, "pet_level_up", {"new_level": new_pet_level},
                )
            # Lifetime XP buckets: fire on each 1000-step boundary cross.
            if (old_total // _XP_MILESTONE_BUCKET) != (
                new_total // _XP_MILESTONE_BUCKET
            ):
                _safe_evaluate_badges(
                    user, "xp_milestone", {"new_total": new_total},
                )
    except IntegrityError:
        return 0

    # Cosmetic unlocks (Block 12): a fresh grant may push total_xp past
    # an xp_threshold. Runs after the committed grant so a cosmetic bug
    # can never roll it back; lazy-imported + self-swallowing, exactly
    # like _safe_evaluate_badges. Skipped on the duplicate path above
    # (no total_xp change to react to).
    from ..cosmetics.service import safe_unlock_cosmetics
    safe_unlock_cosmetics(user)

    return amount


def _safe_evaluate_badges(user, event_name: str, ctx: dict) -> None:
    """Evaluate badges defensively — a badge bug must not roll back an
    otherwise-successful XP grant. Imported lazily to avoid the
    circular import progress.models → xp.service → badges.service →
    progress.models."""
    from ..badges.service import evaluate_badges_for_event
    try:
        evaluate_badges_for_event(user, event_name, ctx)
    except Exception:
        logger.warning(
            "Milestone badge evaluation failed for event=%s", event_name,
            exc_info=True,
        )
