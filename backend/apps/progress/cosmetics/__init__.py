"""Cosmetics foundation: the code-registry catalog (frames, profile
themes, preset avatars) with its four-kind unlock-condition descriptor,
plus the per-student ownership model.

Phase 1 — catalog + model + migration only. No unlock evaluator, no
equip endpoint, no event wiring, no signals (later phases).
"""
from .catalog import (
    COSMETIC_CATALOG,
    CosmeticDef,
    UnlockCondition,
    achievement,
    cosmetics_of_type,
    get_cosmetic,
    list_cosmetics,
    quest_reward,
    starter,
    starter_cosmetics,
    xp_threshold,
)
from .models import StudentCosmetic

__all__ = [
    "COSMETIC_CATALOG",
    "CosmeticDef",
    "UnlockCondition",
    "starter",
    "xp_threshold",
    "achievement",
    "quest_reward",
    "get_cosmetic",
    "list_cosmetics",
    "cosmetics_of_type",
    "starter_cosmetics",
    "StudentCosmetic",
]
