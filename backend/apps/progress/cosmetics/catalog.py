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

The descriptor only *names* the dependency; resolving / granting it is
the evaluator's job (apps.progress.cosmetics.service). The catalog
deliberately does not import the badge or quest catalogs — the
referenced keys are validated by the evaluator at call time, not at
import time, to keep these pure-data modules decoupled.

Every entry belongs to a `collection` (default ``"base"``). The base
collection is the launch catalog below; future themed drops (events,
seasons) get their own collection string without any model change.
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
    # Logical grouping. The launch catalog is all "base"; future drops
    # introduce new collection strings, never a model/migration change.
    collection: str = "base"


COSMETIC_CATALOG: dict[str, CosmeticDef] = {
    # ════════════════════════════ FRAMES (13) ═══════════════════════════════
    # ── Starters (3) ────────────────────────────────────────────────────────
    "frame_plain": CosmeticDef(
        slug="frame_plain",
        type="frame",
        display_name="Ramă simplă",
        asset_ref="frame/plain",
        unlock=starter(),
    ),
    "frame_rounded": CosmeticDef(
        slug="frame_rounded",
        type="frame",
        display_name="Ramă rotunjită",
        asset_ref="frame/rounded",
        unlock=starter(),
    ),
    "frame_dotted": CosmeticDef(
        slug="frame_dotted",
        type="frame",
        display_name="Ramă punctată",
        asset_ref="frame/dotted",
        unlock=starter(),
    ),
    # ── XP thresholds (5) ───────────────────────────────────────────────────
    "frame_iron": CosmeticDef(
        slug="frame_iron",
        type="frame",
        display_name="Ramă de fier",
        asset_ref="frame/iron",
        unlock=xp_threshold(250),
    ),
    "frame_bronze": CosmeticDef(
        slug="frame_bronze",
        type="frame",
        display_name="Ramă de bronz",
        asset_ref="frame/bronze",
        unlock=xp_threshold(1000),
    ),
    "frame_silver": CosmeticDef(
        slug="frame_silver",
        type="frame",
        display_name="Ramă de argint",
        asset_ref="frame/silver",
        unlock=xp_threshold(2500),
    ),
    "frame_gold": CosmeticDef(
        slug="frame_gold",
        type="frame",
        display_name="Ramă de aur",
        asset_ref="frame/gold",
        unlock=xp_threshold(5000),
    ),
    "frame_ornate": CosmeticDef(
        slug="frame_ornate",
        type="frame",
        display_name="Ramă ornată",
        asset_ref="frame/ornate",
        unlock=xp_threshold(10000),
    ),
    # ── Achievements (3) ────────────────────────────────────────────────────
    "frame_laurel": CosmeticDef(
        slug="frame_laurel",
        type="frame",
        display_name="Ramă cu lauri",
        asset_ref="frame/laurel",
        unlock=achievement("unit_1_complete"),
    ),
    "frame_crown": CosmeticDef(
        slug="frame_crown",
        type="frame",
        display_name="Ramă cu coroană",
        asset_ref="frame/crown",
        unlock=achievement("topic_perfect"),
    ),
    "frame_crossed_swords": CosmeticDef(
        slug="frame_crossed_swords",
        type="frame",
        display_name="Ramă cu spade încrucișate",
        asset_ref="frame/crossed_swords",
        unlock=achievement("hard_tier_x5"),
    ),
    # ── Quest rewards (2) ───────────────────────────────────────────────────
    "frame_quest_hunter": CosmeticDef(
        slug="frame_quest_hunter",
        type="frame",
        display_name="Ramă de vânător de misiuni",
        asset_ref="frame/quest_hunter",
        unlock=quest_reward("weekly_quests_claimed"),
    ),
    "frame_whetstone": CosmeticDef(
        slug="frame_whetstone",
        type="frame",
        display_name="Ramă tocilă",
        asset_ref="frame/whetstone",
        unlock=quest_reward("weekly_exercise"),
    ),
    # ════════════════════════════ THEMES (6) ════════════════════════════════
    # ── Starters (2) ────────────────────────────────────────────────────────
    "theme_parchment": CosmeticDef(
        slug="theme_parchment",
        type="profile_theme",
        display_name="Pergament",
        asset_ref="theme/parchment",
        unlock=starter(),
    ),
    "theme_castle_stone": CosmeticDef(
        slug="theme_castle_stone",
        type="profile_theme",
        display_name="Piatră de cetate",
        asset_ref="theme/castle_stone",
        unlock=starter(),
    ),
    # ── Achievements (4) ────────────────────────────────────────────────────
    "theme_old_library": CosmeticDef(
        slug="theme_old_library",
        type="profile_theme",
        display_name="Bibliotecă veche",
        asset_ref="theme/old_library",
        unlock=achievement("unit_fully_explored"),
    ),
    "theme_campfire": CosmeticDef(
        slug="theme_campfire",
        type="profile_theme",
        display_name="Foc de tabără",
        asset_ref="theme/campfire",
        unlock=achievement("streak_30"),
    ),
    "theme_companions_den": CosmeticDef(
        slug="theme_companions_den",
        type="profile_theme",
        display_name="Vizuina companionului",
        asset_ref="theme/companions_den",
        unlock=achievement("pet_level_25"),
    ),
    "theme_throne_room": CosmeticDef(
        slug="theme_throne_room",
        type="profile_theme",
        display_name="Sala tronului",
        asset_ref="theme/throne_room",
        unlock=achievement("xp_milestone_10k"),
    ),
    # ════════════════════════════ AVATARS (8) ═══════════════════════════════
    # ── Starters (2) ────────────────────────────────────────────────────────
    "avatar_apprentice_boy": CosmeticDef(
        slug="avatar_apprentice_boy",
        type="avatar",
        display_name="Ucenic",
        asset_ref="avatar/apprentice_boy",
        unlock=starter(),
    ),
    "avatar_apprentice_girl": CosmeticDef(
        slug="avatar_apprentice_girl",
        type="avatar",
        display_name="Ucenică",
        asset_ref="avatar/apprentice_girl",
        unlock=starter(),
    ),
    # ── XP thresholds (2) ───────────────────────────────────────────────────
    "avatar_squire": CosmeticDef(
        slug="avatar_squire",
        type="avatar",
        display_name="Scutier",
        asset_ref="avatar/squire",
        unlock=xp_threshold(500),
    ),
    "avatar_ranger": CosmeticDef(
        slug="avatar_ranger",
        type="avatar",
        display_name="Cercetaș",
        asset_ref="avatar/ranger",
        unlock=xp_threshold(3000),
    ),
    # ── Achievements (3) ────────────────────────────────────────────────────
    "avatar_champion": CosmeticDef(
        slug="avatar_champion",
        type="avatar",
        display_name="Campion",
        asset_ref="avatar/champion",
        unlock=achievement("test_perfect_score"),
    ),
    "avatar_beast_tamer": CosmeticDef(
        slug="avatar_beast_tamer",
        type="avatar",
        display_name="Îmblânzitor de fiare",
        asset_ref="avatar/beast_tamer",
        unlock=achievement("pet_level_50"),
    ),
    "avatar_steady_learner": CosmeticDef(
        slug="avatar_steady_learner",
        type="avatar",
        display_name="Învățăcel constant",
        asset_ref="avatar/steady_learner",
        unlock=achievement("streak_7"),
    ),
    # ── Quest reward (1) ────────────────────────────────────────────────────
    "avatar_test_collector": CosmeticDef(
        slug="avatar_test_collector",
        type="avatar",
        display_name="Colecționar de teste",
        asset_ref="avatar/test_collector",
        unlock=quest_reward("weekly_test_passed"),
    ),
}


def get_cosmetic(slug: str) -> CosmeticDef | None:
    return COSMETIC_CATALOG.get(slug)


def list_cosmetics() -> list[CosmeticDef]:
    return list(COSMETIC_CATALOG.values())


def cosmetics_of_type(cosmetic_type: CosmeticType) -> list[CosmeticDef]:
    return [c for c in COSMETIC_CATALOG.values() if c.type == cosmetic_type]


def starter_cosmetics() -> list[CosmeticDef]:
    """The cosmetics every student owns from day one (3 frames, 2 themes,
    2 avatars = 7)."""
    return [c for c in COSMETIC_CATALOG.values() if c.unlock.kind == "starter"]
