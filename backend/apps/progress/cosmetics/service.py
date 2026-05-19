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
import uuid

from django.core.files.base import ContentFile
from django.db import transaction

from apps.progress.badges.catalog import CATALOG as BADGE_CATALOG
from apps.progress.models import Achievement
from apps.progress.quests.catalog import QUEST_CATALOG
from apps.progress.quests.models import QuestAssignment
from apps.users.models import StudentProfile

from .avatar import (  # noqa: F401  -- InvalidAvatarUpload re-exported for views
    InvalidAvatarUpload,
    normalize_avatar_upload,
)
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


# ── Read-side: catalog + per-student state ──────────────────────────────────

def owned_slugs(user) -> set[str]:
    """The set of cosmetic slugs this student currently owns.

    The view-side diff (`newly_unlocked_cosmetics`) compares this set
    before vs. after the request. Returns an empty set for non-students,
    so a non-student response carries a stable empty diff.
    """
    profile = _resolve_profile(user)
    if profile is None:
        return set()
    return set(
        StudentCosmetic.objects.filter(student=profile).values_list(
            "cosmetic_slug", flat=True
        )
    )


def _compact_display(cdef) -> dict:
    """Display shape shared by the list endpoint and the per-request
    unlock diff. Locked / unlock metadata is added by the list builder."""
    return {
        "slug": cdef.slug,
        "type": cdef.type,
        "display_name": cdef.display_name,
        "asset_ref": cdef.asset_ref,
        "collection": cdef.collection,
    }


def serialize_cosmetics(slugs) -> list[dict]:
    """Resolve an iterable of slugs into the compact display dicts the
    list endpoint uses for `newly_unlocked_cosmetics`. Catalog ordering;
    unknown slugs (e.g. catalog drift) are skipped defensively.
    """
    requested = set(slugs)
    return [
        _compact_display(cdef)
        for slug, cdef in COSMETIC_CATALOG.items()
        if slug in requested
    ]


def _unlock_display(cond: UnlockCondition) -> dict | None:
    """Resolve a locked cosmetic's `UnlockCondition` into the displayable
    payload the list endpoint exposes.

    Runtime catalog lookups (the badge and quest catalogs are imported
    at module top, but the *values* are read here so a catalog edit is
    picked up without restart). A starter cosmetic has no displayable
    requirement — it's owned the moment a profile is provisioned — so
    None is returned. Unknown badge/quest references degrade to the raw
    key; the displayable surface never raises on catalog drift.
    """
    if cond.kind == "starter":
        return None
    if cond.kind == "xp_threshold":
        return {"kind": "xp_threshold", "xp": cond.xp}
    if cond.kind == "achievement":
        badge = BADGE_CATALOG.get(cond.badge_key)
        return {
            "kind": "achievement",
            "badge_key": cond.badge_key,
            "label": badge.name if badge is not None else cond.badge_key,
        }
    if cond.kind == "quest_reward":
        quest = QUEST_CATALOG.get(cond.quest_slug)
        return {
            "kind": "quest_reward",
            "quest_slug": cond.quest_slug,
            "label": quest.title if quest is not None else cond.quest_slug,
        }
    return None


def _avatar_state(profile) -> dict:
    """The shared `avatar_source` + `avatar_image_url` block.

    Centralised so the four endpoints that surface avatar state (list,
    equip, upload, source-switch) all expose the same shape. A non-
    student or a profile without an upload still returns the keys —
    just with None values — so the frontend never has to branch on
    presence vs. absence.
    """
    if profile is None:
        return {"avatar_source": None, "avatar_image_url": None}
    img = profile.avatar_image
    # `bool(ImageField)` is False when no file is associated; `.url`
    # raises on an empty field, so guard it.
    return {
        "avatar_source": profile.avatar_source,
        "avatar_image_url": img.url if img else None,
    }


def build_catalog_state(user) -> dict:
    """The list endpoint body: every catalog entry annotated with this
    student's owned/equipped state, plus a snapshot of the currently
    equipped cosmetic per type and the avatar block
    (`avatar_source` + `avatar_image_url`).

    One cosmetic-rows query, one profile fetch (already done by
    `_resolve_profile`). For a non-student the per-student annotations
    flatten to all-false / no equips, so the catalog is still browsable.
    """
    profile = _resolve_profile(user)
    if profile is None:
        owned_state: dict[str, bool] = {}
    else:
        rows = StudentCosmetic.objects.filter(student=profile).values_list(
            "cosmetic_slug", "is_equipped"
        )
        owned_state = {slug: is_eq for slug, is_eq in rows}

    equipped_by_type: dict[str, str | None] = {
        "frame": None,
        "profile_theme": None,
        "avatar": None,
    }

    cosmetics: list[dict] = []
    for cdef in COSMETIC_CATALOG.values():
        equipped = owned_state.get(cdef.slug, False) is True
        owned = cdef.slug in owned_state
        if equipped:
            equipped_by_type[cdef.type] = cdef.slug
        entry = _compact_display(cdef)
        entry["owned"] = owned
        entry["equipped"] = equipped
        # Show the requirement only for locked entries — owned cosmetics
        # have nothing left to gate on.
        entry["unlock"] = None if owned else _unlock_display(cdef.unlock)
        cosmetics.append(entry)

    return {
        "cosmetics": cosmetics,
        "equipped": equipped_by_type,
        **_avatar_state(profile),
    }


# ── Equip path ──────────────────────────────────────────────────────────────

class CosmeticEquipError(Exception):
    """An equip was rejected. Carries the Romanian message and the HTTP
    status the view should surface (mirrors quests.service.QuestClaimError)."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def equip_cosmetic(user, slug: str) -> dict:
    """Equip `slug` for `user`. Returns the post-equip state shape used
    by the list endpoint's `equipped` / `avatar_source` keys.

    Ownership is enforced — equipping requires the student already owns
    the cosmetic. The one-equipped-per-type invariant is held with a
    transactional clear-then-set: the currently-equipped row of that
    type is un-equipped first so the `uniq_one_equipped_per_type`
    partial index can never reject the new equip. For an avatar-type
    equip the profile's `avatar_source` is flipped to PRESET in the
    same transaction so the displayed avatar resolves to the preset.
    Frames and themes end up with exactly one equipped; avatars may
    still have none (no auto-equip elsewhere).

    Raises CosmeticEquipError on unknown slug (404) or unowned cosmetic
    (403). Re-equipping the already-equipped cosmetic is a no-op
    success — no exception, returned state reflects current reality.
    """
    profile = _resolve_profile(user)
    if profile is None:
        raise CosmeticEquipError("Doar elevii pot echipa cosmetice.", 403)

    cdef = COSMETIC_CATALOG.get(slug)
    if cdef is None:
        raise CosmeticEquipError("Cosmeticul nu există.", 404)

    target = (
        StudentCosmetic.objects.filter(student=profile, cosmetic_slug=slug)
        .first()
    )
    if target is None:
        raise CosmeticEquipError("Nu deții acest cosmetic.", 403)

    with transaction.atomic():
        # Clear-then-set under one transaction so the partial unique
        # index `uniq_one_equipped_per_type` is never in a momentarily-
        # double-equipped state. Excluding the target itself keeps the
        # re-equip-current-cosmetic case a clean no-op.
        StudentCosmetic.objects.filter(
            student=profile,
            cosmetic_type=cdef.type,
            is_equipped=True,
        ).exclude(pk=target.pk).update(is_equipped=False)
        if not target.is_equipped:
            target.is_equipped = True
            target.save(update_fields=["is_equipped"])

        # An avatar equip also switches the source so the displayed
        # avatar actually resolves to the preset. Other types don't
        # touch the profile — they layer onto whatever source is active.
        if cdef.type == "avatar" and profile.avatar_source != (
            StudentProfile.AvatarSource.PRESET
        ):
            profile.avatar_source = StudentProfile.AvatarSource.PRESET
            profile.save(update_fields=["avatar_source"])

    # Fresh state snapshot — single query, mirrors build_catalog_state.
    equipped_rows = StudentCosmetic.objects.filter(
        student=profile, is_equipped=True
    ).values_list("cosmetic_type", "cosmetic_slug")
    equipped_by_type: dict[str, str | None] = {
        "frame": None,
        "profile_theme": None,
        "avatar": None,
    }
    for t, s in equipped_rows:
        equipped_by_type[t] = s
    profile.refresh_from_db(fields=["avatar_source"])
    return {
        "equipped": equipped_by_type,
        **_avatar_state(profile),
    }


# ── Avatar upload + source switching ────────────────────────────────────────

class AvatarSourceError(Exception):
    """An avatar-source switch was rejected. Carries the Romanian
    message and the HTTP status the view should surface (mirrors
    CosmeticEquipError / QuestClaimError)."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def upload_avatar(user, uploaded_file) -> dict:
    """Validate + normalise an uploaded avatar, persist it, and flip
    `avatar_source` to UPLOAD. Returns the post-upload avatar state.

    Replaces any previously-stored avatar — the old file is deleted from
    storage before the new one is saved so we don't accumulate orphans.
    The stored filename is a fresh UUID, never derived from what the
    student uploaded (defence-in-depth against path-traversal and
    information leakage). The InvalidAvatarUpload raised by the
    normaliser propagates to the view as-is so the 400 reason is the
    pipeline's own Romanian message.
    """
    profile = _resolve_profile(user)
    if profile is None:
        raise AvatarSourceError("Doar elevii pot încărca avatare.", 403)

    data, ext = normalize_avatar_upload(uploaded_file)

    # Delete the previous file first. Best-effort: a storage hiccup
    # here shouldn't block the new upload — we'd rather have an orphan
    # than reject a valid replacement.
    if profile.avatar_image:
        try:
            profile.avatar_image.delete(save=False)
        except Exception:
            logger.warning(
                "Failed to delete previous avatar for profile #%s",
                profile.pk,
                exc_info=True,
            )

    filename = f"{uuid.uuid4().hex}.{ext}"
    # ImageField.save() routes through `field.generate_filename`, which
    # prepends `upload_to="avatars/"` — the resulting path on disk is
    # MEDIA_ROOT/avatars/<uuid>.<ext>.
    profile.avatar_image.save(filename, ContentFile(data), save=False)
    profile.avatar_source = StudentProfile.AvatarSource.UPLOAD
    profile.save(update_fields=["avatar_image", "avatar_source"])
    return _avatar_state(profile)


def set_avatar_source(user, source: str) -> dict:
    """Switch the displayed-avatar source.

    Validates that the requested source is reachable given the
    student's current state:
    - MONOGRAM is always available — every student can fall back to it.
    - UPLOAD requires a stored `avatar_image`.
    - PRESET requires an equipped avatar-type cosmetic. (Equipping an
      avatar already flips the source to PRESET in equip_cosmetic, so
      this endpoint mainly covers moving *back* to MONOGRAM or to an
      existing UPLOAD.)
    """
    profile = _resolve_profile(user)
    if profile is None:
        raise AvatarSourceError(
            "Doar elevii au sursă de avatar.", 403,
        )

    valid_sources = {choice.value for choice in StudentProfile.AvatarSource}
    if source not in valid_sources:
        raise AvatarSourceError("Sursă de avatar invalidă.", 400)

    if source == StudentProfile.AvatarSource.UPLOAD and not profile.avatar_image:
        raise AvatarSourceError(
            "Nu există o imagine încărcată — încarcă una mai întâi.",
            400,
        )

    if source == StudentProfile.AvatarSource.PRESET:
        has_avatar_equipped = StudentCosmetic.objects.filter(
            student=profile,
            cosmetic_type="avatar",
            is_equipped=True,
        ).exists()
        if not has_avatar_equipped:
            raise AvatarSourceError(
                "Echipează mai întâi un avatar preset.", 400,
            )

    if profile.avatar_source != source:
        profile.avatar_source = source
        profile.save(update_fields=["avatar_source"])
    return _avatar_state(profile)
