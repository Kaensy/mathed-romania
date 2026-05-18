"""Quests foundation: the daily/weekly catalog, the tunable points
economy, and the two per-student state models.

Phase 1 — catalog + config + models + migration only. No endpoints,
no event wiring, no assignment/claim logic (Phase 2).

`periods` is intentionally NOT re-exported here: it imports
`streak_service` (→ `progress.models`), and this package's `__init__`
runs during model registration, before `progress.models` finishes
importing. Import it directly: `from apps.progress.quests.periods import ...`.
"""
from .catalog import (
    DAILY_MILESTONES,
    DEFAULT_DAILY_POINTS,
    QUEST_CATALOG,
    QuestDef,
    daily_quests,
    get_quest,
    list_quests,
    weekly_quests,
)
from .models import DailyChallengeProgress, QuestAssignment

__all__ = [
    "QUEST_CATALOG",
    "QuestDef",
    "DEFAULT_DAILY_POINTS",
    "DAILY_MILESTONES",
    "get_quest",
    "list_quests",
    "daily_quests",
    "weekly_quests",
    "QuestAssignment",
    "DailyChallengeProgress",
]
