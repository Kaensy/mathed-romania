"""XP foundation: append-only ledger, declarative awards registry,
and the `award_xp` helper that wires the two together.

No view wiring or pet system here — those land in later phases.
"""
from .awards import XP_AWARDS
from .models import XPLedger
from .service import award_xp, student_grade

__all__ = ["XP_AWARDS", "XPLedger", "award_xp", "student_grade"]
