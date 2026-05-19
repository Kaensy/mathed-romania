"""
Cosmetic catalog — single source of truth for every unlockable cosmetic.

Mirrors the Block 9 badge catalog / Block 10 XP awards / Block 11 quest
catalog shape: declarative, self-describing, and migration-free. The
StudentCosmetic model stores `cosmetic_slug` (and a snapshotted
`cosmetic_type`) as free-form CharFields, so adding or editing a cosmetic
here never requires a database migration.

Three cosmetic types ship:

- ``frame``         — decorative border around the avatar
- ``profile_theme`` — color/skin applied to the profile surface
- ``avatar``        — a preset avatar image (one of the three avatar
                      sources on StudentProfile; see users.StudentProfile)

Every entry carries an `UnlockCondition` descriptor. Four kinds are
expressible:

- ``starter``       — free, owned by every student from day one
- ``xp_threshold``  — unlocked once lifetime XP reaches `xp`
- ``achievement``   — unlocked when the `badge_key` badge is earned
                      (a key from apps.progress.badges.catalog.CATALOG)
- ``quest_reward``  — unlocked as the reward of `quest_slug`
                      (a slug from apps.progress.quests.catalog.QUEST_CATALOG)

The descriptor only *names* the dependency; resolving / evaluating it is
a later phase. There is intentionally no unlock evaluator here, and the
catalog deliberately does not import the badge or quest catalogs — the
referenced keys are validated by the (future) evaluator, not at import
time, to keep these pure-data modules decoupled.

Slugs, names and asset references below are placeholders — the full
catalog lands next phase. They exist so the models can be migrated and
exercised.
"""
from dataclasses import dataclass
from typing import Literal

CosmeticType = Literal["frame", "profile_theme", "avatar"]
UnlockKind = Literal["starter", "xp_threshold", "achievement", "quest_reward"]


@dataclass(frozen=True)
class UnlockCondition:
    """How a cosmetic becomes owned.

    Exactly one of the optional fields is meaningful, selected by `kind`:
    - kind="starter"       → no extra fields (owned by default)
    - kind="xp_threshold"  → `xp` is the minimum lifetime XP
    - kind="achievement"   → `badge_key` references badges.CATALOG
    - kind="quest_reward"  → `quest_slug` references QUEST_CATALOG

    Use the module-level constructors (`starter()`, `xp_threshold()`,
    `achievement()`, `quest_reward()`) instead of instantiating directly,
    so the right field is always paired with the right kind.
    """

    kind: UnlockKind
    xp: int | None = None
    badge_key: str | None = None
    quest_slug: str | None = None


def starter() -> UnlockCondition:
    return UnlockCondition(kind="starter")


def xp_threshold(xp: int) -> UnlockCondition:
    return UnlockCondition(kind="xp_threshold", xp=xp)


def achievement(badge_key: str) -> UnlockCondition:
    return UnlockCondition(kind="achievement", badge_key=badge_key)


def quest_reward(quest_slug: str) -> UnlockCondition:
    return UnlockCondition(kind="quest_reward", quest_slug=quest_slug)


@dataclass(frozen=True)
class CosmeticDef:
    slug: str
    type: CosmeticType
    display_name: str
    # Opaque asset reference resolved by the frontend: a CSS theme key,
    # a frame style key, or a preset-avatar image key. Format is
    # type-specific and not interpreted by the backend.
    asset_ref: str
    unlock: UnlockCondition


COSMETIC_CATALOG: dict[str, CosmeticDef] = {
    # ── Frames ──────────────────────────────────────────────────────────────
    "frame_starter": CosmeticDef(
        slug="frame_starter",
        type="frame",
        display_name="Ramă simplă",
        asset_ref="frame/starter",
        unlock=starter(),
    ),
    "frame_bronze": CosmeticDef(
        slug="frame_bronze",
        type="frame",
        display_name="Ramă de bronz",
        asset_ref="frame/bronze",
        unlock=xp_threshold(1000),
    ),
    "frame_scholar": CosmeticDef(
        slug="frame_scholar",
        type="frame",
        display_name="Ramă de cărturar",
        asset_ref="frame/scholar",
        unlock=achievement("topic_perfect"),
    ),
    # ── Profile themes ──────────────────────────────────────────────────────
    "theme_starter": CosmeticDef(
        slug="theme_starter",
        type="profile_theme",
        display_name="Temă implicită",
        asset_ref="theme/starter",
        unlock=starter(),
    ),
    "theme_ocean": CosmeticDef(
        slug="theme_ocean",
        type="profile_theme",
        display_name="Temă oceanică",
        asset_ref="theme/ocean",
        unlock=xp_threshold(5000),
    ),
    "theme_marathoner": CosmeticDef(
        slug="theme_marathoner",
        type="profile_theme",
        display_name="Temă maratonist",
        asset_ref="theme/marathoner",
        unlock=quest_reward("weekly_exercise"),
    ),
    # ── Preset avatars ──────────────────────────────────────────────────────
    "avatar_starter": CosmeticDef(
        slug="avatar_starter",
        type="avatar",
        display_name="Avatar implicit",
        asset_ref="avatar/starter",
        unlock=starter(),
    ),
    "avatar_fox": CosmeticDef(
        slug="avatar_fox",
        type="avatar",
        display_name="Vulpe isteață",
        asset_ref="avatar/fox",
        unlock=xp_threshold(2000),
    ),
    "avatar_owl": CosmeticDef(
        slug="avatar_owl",
        type="avatar",
        display_name="Bufniță înțeleaptă",
        asset_ref="avatar/owl",
        unlock=achievement("streak_7"),
    ),
}


def get_cosmetic(slug: str) -> CosmeticDef | None:
    return COSMETIC_CATALOG.get(slug)


def list_cosmetics() -> list[CosmeticDef]:
    return list(COSMETIC_CATALOG.values())


def cosmetics_of_type(cosmetic_type: CosmeticType) -> list[CosmeticDef]:
    return [c for c in COSMETIC_CATALOG.values() if c.type == cosmetic_type]


def starter_cosmetics() -> list[CosmeticDef]:
    """The cosmetics every student owns from day one (one per type)."""
    return [c for c in COSMETIC_CATALOG.values() if c.unlock.kind == "starter"]
