"""
Quest catalog — single source of truth for daily and weekly quests.

Mirrors the Block 9 badge catalog and Block 10 XP awards shape:
declarative, self-describing, and migration-free. QuestAssignment stores
`quest_slug` as a free-form CharField, so adding or editing a quest here
never requires a database migration. Existing in-flight assignments are
unaffected by catalog edits because they snapshot `target` at creation
(see QuestAssignment in .models).

Every XP / point amount below is a tunable module constant — change the
numbers, not the call sites.
"""
from dataclasses import dataclass
from typing import Literal

Cadence = Literal["daily", "weekly"]

# Phase-2 event slugs. The goal_type on a quest names the event whose
# emission advances that quest's progress. Kept as a Literal so the
# catalog and the (future) event dispatcher can't drift apart silently.
GoalType = Literal[
    "login",
    "daily_test_started",
    "daily_test_completed",
    "exercise_completed",
    "test_passed",
    "daily_quest_claimed",
]

# ── Tunable economy constants ───────────────────────────────────────────────

# Points a single claimed daily quest contributes to the daily points
# bar. 5 daily quests × 20 = 100, which is the top DAILY_MILESTONES rung.
DEFAULT_DAILY_POINTS = 20

# XP paid out when a daily quest is claimed (uniform across the 5).
DAILY_QUEST_XP = 10

# XP paid out per weekly quest. Weekly goals are scaled-up versions of
# the daily ones, so the rewards are larger and tuned per-quest.
WEEKLY_LOGIN_XP = 50
WEEKLY_TEST_STARTED_XP = 50
WEEKLY_TEST_COMPLETED_XP = 80
WEEKLY_EXERCISE_XP = 120
WEEKLY_TEST_PASSED_XP = 100
WEEKLY_QUESTS_CLAIMED_XP = 150

# Daily points-bar milestones: (threshold, xp_reward). 20/40/60/80 are
# the small rungs, 100 is the large finale. No ordering is assumed by
# consumers — DailyChallengeProgress tracks claimed thresholds as a set.
DAILY_MILESTONE_SMALL_XP = 15
DAILY_MILESTONE_LARGE_XP = 75
DAILY_MILESTONES: list[tuple[int, int]] = [
    (20, DAILY_MILESTONE_SMALL_XP),
    (40, DAILY_MILESTONE_SMALL_XP),
    (60, DAILY_MILESTONE_SMALL_XP),
    (80, DAILY_MILESTONE_SMALL_XP),
    (100, DAILY_MILESTONE_LARGE_XP),
]


@dataclass(frozen=True)
class QuestDef:
    slug: str
    cadence: Cadence
    goal_type: GoalType
    title: str
    description: str
    target_count: int
    xp_reward: int
    # Points contributed to the daily bar when claimed. Daily quests
    # only — weekly quests leave this None.
    point_value: int | None = None


QUEST_CATALOG: dict[str, QuestDef] = {
    # ── Daily set (5 fixed quests, target 1, point_value=DEFAULT_DAILY_POINTS) ──
    "daily_login": QuestDef(
        slug="daily_login",
        cadence="daily",
        goal_type="login",
        title="Prezent!",
        description="Conectează-te în aplicație astăzi.",
        target_count=1,
        xp_reward=DAILY_QUEST_XP,
        point_value=DEFAULT_DAILY_POINTS,
    ),
    "daily_test_start": QuestDef(
        slug="daily_test_start",
        cadence="daily",
        goal_type="daily_test_started",
        title="Start la testul zilnic",
        description="Începe testul zilnic de astăzi.",
        target_count=1,
        xp_reward=DAILY_QUEST_XP,
        point_value=DEFAULT_DAILY_POINTS,
    ),
    "daily_test_finish": QuestDef(
        slug="daily_test_finish",
        cadence="daily",
        goal_type="daily_test_completed",
        title="Test zilnic terminat",
        description="Termină testul zilnic de astăzi.",
        target_count=1,
        xp_reward=DAILY_QUEST_XP,
        point_value=DEFAULT_DAILY_POINTS,
    ),
    "daily_exercise": QuestDef(
        slug="daily_exercise",
        cadence="daily",
        goal_type="exercise_completed",
        title="Exercițiu rezolvat",
        description="Rezolvă corect un exercițiu de practică.",
        target_count=1,
        xp_reward=DAILY_QUEST_XP,
        point_value=DEFAULT_DAILY_POINTS,
    ),
    "daily_test_passed": QuestDef(
        slug="daily_test_passed",
        cadence="daily",
        goal_type="test_passed",
        title="Test promovat",
        description="Promovează un test de subiect sau de unitate.",
        target_count=1,
        xp_reward=DAILY_QUEST_XP,
        point_value=DEFAULT_DAILY_POINTS,
    ),
    # No Daily Raid quest — Raids don't exist yet. It joins the catalog
    # when the Raid subsystem lands.

    # ── Weekly set (scaled-up goals, larger xp, no point_value) ─────────────
    "weekly_login": QuestDef(
        slug="weekly_login",
        cadence="weekly",
        goal_type="login",
        title="Săptămână activă",
        description="Conectează-te în 5 zile diferite din această săptămână.",
        target_count=5,
        xp_reward=WEEKLY_LOGIN_XP,
    ),
    "weekly_test_start": QuestDef(
        slug="weekly_test_start",
        cadence="weekly",
        goal_type="daily_test_started",
        title="Obișnuința testului zilnic",
        description="Începe testul zilnic în 5 zile din această săptămână.",
        target_count=5,
        xp_reward=WEEKLY_TEST_STARTED_XP,
    ),
    "weekly_test_finish": QuestDef(
        slug="weekly_test_finish",
        cadence="weekly",
        goal_type="daily_test_completed",
        title="Maraton de teste zilnice",
        description="Termină testul zilnic în 5 zile din această săptămână.",
        target_count=5,
        xp_reward=WEEKLY_TEST_COMPLETED_XP,
    ),
    "weekly_exercise": QuestDef(
        slug="weekly_exercise",
        cadence="weekly",
        goal_type="exercise_completed",
        title="Antrenament intens",
        description="Rezolvă corect 30 de exerciții de practică în această săptămână.",
        target_count=30,
        xp_reward=WEEKLY_EXERCISE_XP,
    ),
    "weekly_test_passed": QuestDef(
        slug="weekly_test_passed",
        cadence="weekly",
        goal_type="test_passed",
        title="Colecționar de teste",
        description="Promovează 5 teste de subiect sau de unitate în această săptămână.",
        target_count=5,
        xp_reward=WEEKLY_TEST_PASSED_XP,
    ),
    "weekly_quests_claimed": QuestDef(
        slug="weekly_quests_claimed",
        cadence="weekly",
        goal_type="daily_quest_claimed",
        title="Vânător de misiuni",
        description="Revendică 20 de misiuni zilnice în această săptămână.",
        target_count=20,
        xp_reward=WEEKLY_QUESTS_CLAIMED_XP,
    ),
}


def get_quest(slug: str) -> QuestDef | None:
    return QUEST_CATALOG.get(slug)


def list_quests() -> list[QuestDef]:
    return list(QUEST_CATALOG.values())


def daily_quests() -> list[QuestDef]:
    return [q for q in QUEST_CATALOG.values() if q.cadence == "daily"]


def weekly_quests() -> list[QuestDef]:
    return [q for q in QUEST_CATALOG.values() if q.cadence == "weekly"]
