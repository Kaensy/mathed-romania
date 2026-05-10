"""
Pet level derivation.

Placeholder curve: `level = floor(sqrt(xp / K)) + 1`, K is a tunable
constant that controls how slowly XP-per-level grows. K is sized so that
fully completing Grade 5 lands a student around level ~100 — once
Units 2+ ship and we have real per-grade XP totals, we'll re-tune K
(and possibly switch to a piecewise curve) without changing the public
function signature.

Inverse of the level curve:
  threshold(L) = (L - 1)^2 * K
i.e. the minimum XP required to be at level L.
"""
from math import floor, sqrt

# Tunable. Larger K = slower leveling. Targets ~100 levels at full
# Grade 5 completion using current placeholder XP_AWARDS amounts.
K: int = 50


def level_for_xp(xp: int) -> int:
    """Map an XP total to a 1-indexed level. Always returns >= 1."""
    if xp <= 0:
        return 1
    return floor(sqrt(xp / K)) + 1


def _threshold_for_level(level: int) -> int:
    """Minimum XP to be at `level` (level 1 starts at 0)."""
    if level <= 1:
        return 0
    return (level - 1) ** 2 * K


def xp_to_next_level(current_xp: int) -> int:
    """XP gap from `current_xp` up to the threshold for the next level."""
    next_level = level_for_xp(current_xp) + 1
    return _threshold_for_level(next_level) - max(current_xp, 0)
