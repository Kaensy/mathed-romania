"""Cosmetic unlock evaluator.

`unlock_cosmetics` is the single entry point: given a student it grants
every not-yet-owned catalog cosmetic whose unlock condition is satisfied
by the student's *current* state — lifetime `total_xp`, earned badges,
and claimed quests. It is a full idempotent re-evaluation, so crossing
several thresholds in one XP grant simply unlocks several cosmetics, and
a repeat call is a pure no-op.

Unlocking only creates an owned StudentCosmetic row — it never
auto-equips. Equipping is an explicit user action for a later phase. No
XP and no badges are awarded for unlocking a cosmetic.

`safe_unlock_cosmetics` is the swallowing wrapper the three Block-12 hook
sites use (mirrors xp.service._safe_evaluate_badges): a cosmetic bug must
never roll back the XP grant, badge creation, or quest claim that
triggered it. Every call site lazy-imports from this module so the known
progress.models → xp.service → badges.service import chain is not
extended.

This module is only ever lazy-imported (from the hook sites and the
registration serializer), so its top-level model imports run well after
the app registry is ready — the same discipline as quests.service.
"""
import logging

from apps.progress.models import Achievement
from apps.progress.quests.models import QuestAssignment
from apps.users.models import StudentProfile

from .catalog import COSMETIC_CATALOG, UnlockCondition
from .models import StudentCosmetic

logger = logging.getLogger(__name__)

# The two cosmetics every student always has equipped. Avatars are
# intentionally absent — avatar_source defaults to MONOGRAM, so a student
# always shows *something* without a default-equipped preset avatar.
DEFAULT_FRAME_SLUG = "frame_plain"  # the plainest starter frame
DEFAULT_THEME_SLUG = "theme_parchment"  # the parchment starter theme


def _resolve_profile(user):
    """StudentProfile for `user`, or None for non-students.

    Mirrors award_xp / quests.service resolution so cosmetic wiring
    degrades the same way XP and quest wiring do for a non-student
    caller.
    """
    return StudentProfile.objects.filter(user=user).first()


def _condition_met(
    cond: UnlockCondition,
    total_xp: int,
    earned_badges: set[str],
    claimed_quests: set[str],
) -> bool:
    if cond.kind == "starter":
        return True
    if cond.kind == "xp_threshold":
        return cond.xp is not None and total_xp >= cond.xp
    if cond.kind == "achievement":
        return cond.badge_key in earned_badges
    if cond.kind == "quest_reward":
        return cond.quest_slug in claimed_quests
    return False


def unlock_cosmetics(user) -> list[str]:
    """Grant every satisfied, not-yet-owned cosmetic. Returns the slugs
    newly unlocked (advisory — no Phase-2 caller consumes it yet).

    Reads the student's whole current state once, then per-candidate
    `get_or_create` (idempotent, race-safe via the
    (student, cosmetic_slug) unique constraint). Never equips: rows are
    always created with is_equipped=False. Does not swallow exceptions —
    use `safe_unlock_cosmetics` from hook sites.
    """
    profile = _resolve_profile(user)
    if profile is None:
        return []

    total_xp = profile.total_xp
    earned_badges = set(
        Achievement.objects.filter(student=user).values_list(
            "badge_key", flat=True
        )
    )
    claimed_quests = set(
        QuestAssignment.objects.filter(
            student=profile, status=QuestAssignment.Status.CLAIMED
        ).values_list("quest_slug", flat=True)
    )
    owned = set(
        StudentCosmetic.objects.filter(student=profile).values_list(
            "cosmetic_slug", flat=True
        )
    )

    newly: list[str] = []
    for slug, cdef in COSMETIC_CATALOG.items():
        if slug in owned:
            continue
        if not _condition_met(
            cdef.unlock, total_xp, earned_badges, claimed_quests
        ):
            continue
        _, created = StudentCosmetic.objects.get_or_create(
            student=profile,
            cosmetic_slug=slug,
            defaults={"cosmetic_type": cdef.type, "is_equipped": False},
        )
        if created:
            newly.append(slug)
    return newly


def _ensure_default_equipped(profile) -> None:
    """Guarantee the student owns and has equipped the plainest starter
    frame and the parchment theme.

    Equips a default only when *nothing* of that type is currently
    equipped, so this is idempotent and never overrides a future
    explicit equip choice. Avatars get no default-equip by design.
    """
    for slug in (DEFAULT_FRAME_SLUG, DEFAULT_THEME_SLUG):
        cdef = COSMETIC_CATALOG[slug]
        owned_row, _ = StudentCosmetic.objects.get_or_create(
            student=profile,
            cosmetic_slug=slug,
            defaults={"cosmetic_type": cdef.type, "is_equipped": False},
        )
        type_has_equipped = StudentCosmetic.objects.filter(
            student=profile,
            cosmetic_type=cdef.type,
            is_equipped=True,
        ).exists()
        if not type_has_equipped:
            owned_row.is_equipped = True
            owned_row.save(update_fields=["is_equipped"])


def provision_student_cosmetics(user) -> list[str]:
    """Full cosmetic provisioning for one student: run the evaluator,
    then ensure the two defaults are equipped.

    Used both at student-profile creation and by the one-time backfill.
    Idempotent: a re-run grants nothing new and re-equips nothing.
    """
    profile = _resolve_profile(user)
    if profile is None:
        return []
    newly = unlock_cosmetics(user)
    _ensure_default_equipped(profile)
    return newly


def safe_unlock_cosmetics(user) -> list[str]:
    """Self-swallowing wrapper for the Block-12 hook sites. A cosmetic
    failure is logged, never propagated — it must not roll back the XP
    grant / badge creation / quest claim that triggered it (mirrors
    xp.service._safe_evaluate_badges)."""
    try:
        return unlock_cosmetics(user)
    except Exception:
        logger.warning("Cosmetic unlock evaluation failed", exc_info=True)
        return []


def safe_provision_student_cosmetics(user) -> list[str]:
    """Self-swallowing wrapper for the registration path — a cosmetic
    hiccup must never fail student sign-up."""
    try:
        return provision_student_cosmetics(user)
    except Exception:
        logger.warning("Cosmetic provisioning failed", exc_info=True)
        return []
