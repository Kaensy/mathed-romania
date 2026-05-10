"""
Badge catalog — single source of truth for all achievements.

Adding or editing a badge here never requires a database migration; the
Achievement model stores `badge_key` as a free-form CharField.
"""
from dataclasses import dataclass
from typing import Literal

BadgeFamily = Literal["progress", "mastery", "consistency", "discovery"]


@dataclass(frozen=True)
class BadgeDef:
    key: str
    family: BadgeFamily
    name: str
    description: str
    icon_name: str
    secret: bool = False


CATALOG: dict[str, BadgeDef] = {
    "first_lesson_opened": BadgeDef(
        key="first_lesson_opened",
        family="progress",
        name="Primii pași",
        description="Ai deschis prima ta lecție și ai pornit la drum.",
        icon_name="footprint",
    ),
    "first_topic_test_passed": BadgeDef(
        key="first_topic_test_passed",
        family="progress",
        name="Început puternic",
        description="Ai promovat primul test de subiect.",
        icon_name="medal",
    ),
    "unit_1_complete": BadgeDef(
        key="unit_1_complete",
        family="progress",
        name="Cunoscător al Unității 1",
        description="Ai trecut testul Unității 1 cu succes.",
        icon_name="scroll",
    ),
    "topic_stapanit": BadgeDef(
        key="topic_stapanit",
        family="mastery",
        name="Topic Stăpânit",
        description="Ai atins nivelul Stăpânit la un subiect.",
        icon_name="star",
    ),
    "topic_perfect": BadgeDef(
        key="topic_perfect",
        family="mastery",
        name="Topic Perfect",
        description="Ai atins nivelul Perfect la un subiect.",
        icon_name="crown",
    ),
    "test_perfect_score": BadgeDef(
        key="test_perfect_score",
        family="mastery",
        name="Punctaj Maxim",
        description="Ai obținut nota 10 la un test.",
        icon_name="trophy",
    ),
    "medium_tier_x5": BadgeDef(
        key="medium_tier_x5",
        family="mastery",
        name="Cinci Categorii Medii",
        description="Ai terminat tier-ul Mediu la cinci categorii diferite.",
        icon_name="gem",
    ),
    "hard_tier_x5": BadgeDef(
        key="hard_tier_x5",
        family="mastery",
        name="Maestru al Categoriilor",
        description="Ai terminat tier-ul Greu la cinci categorii diferite.",
        icon_name="sword",
    ),
    "streak_3": BadgeDef(
        key="streak_3",
        family="consistency",
        name="Trei Zile la Rând",
        description="Ai învățat trei zile la rând.",
        icon_name="flame",
    ),
    "streak_7": BadgeDef(
        key="streak_7",
        family="consistency",
        name="Săptămână Întreagă",
        description="Ai ținut o serie de șapte zile consecutive.",
        icon_name="calendar",
    ),
    "streak_30": BadgeDef(
        key="streak_30",
        family="consistency",
        name="Lună Consecventă",
        description="Ai învățat treizeci de zile fără pauză.",
        icon_name="comet",
    ),
    "unit_fully_explored": BadgeDef(
        key="unit_fully_explored",
        family="discovery",
        name="Explorator de Unitate",
        description="Ai deschis fiecare lecție dintr-o unitate.",
        icon_name="compass",
    ),
    "glossary_first_open": BadgeDef(
        key="glossary_first_open",
        family="discovery",
        name="Bibliotecar",
        description="Ai descoperit glosarul pentru prima dată.",
        icon_name="book",
        secret=True,
    ),
    # ── Pet level milestones (Block 10 Phase 6) ──────────────────────────
    "pet_level_10": BadgeDef(
        key="pet_level_10",
        family="mastery",
        name="Companion crescut",
        description="Animalul tău de companie a ajuns la nivelul 10.",
        icon_name="paw",
    ),
    "pet_level_25": BadgeDef(
        key="pet_level_25",
        family="mastery",
        name="Companion devotat",
        description="Animalul tău de companie a ajuns la nivelul 25.",
        icon_name="wolf_howl",
    ),
    "pet_level_50": BadgeDef(
        key="pet_level_50",
        family="mastery",
        name="Companion legendar",
        description="Animalul tău de companie a ajuns la nivelul 50.",
        icon_name="wolf_head",
    ),
    # ── Lifetime XP milestones (Block 10 Phase 6) ────────────────────────
    "xp_milestone_1k": BadgeDef(
        key="xp_milestone_1k",
        family="progress",
        name="Mii de pași",
        description="Ai adunat 1.000 XP în total.",
        icon_name="sparkles",
    ),
    "xp_milestone_10k": BadgeDef(
        key="xp_milestone_10k",
        family="progress",
        name="Zeci de mii",
        description="Ai adunat 10.000 XP în total.",
        icon_name="crystal_growth",
    ),
}


def get_badge(key: str) -> BadgeDef | None:
    return CATALOG.get(key)


def list_badges() -> list[BadgeDef]:
    return list(CATALOG.values())
