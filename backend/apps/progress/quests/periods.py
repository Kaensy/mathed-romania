"""
Period-key derivation for quest assignments.

A QuestAssignment is scoped to the Europe/Bucharest day (daily) or ISO
week (weekly) it belongs to. The single source of "what day is it" is the
streak service — we reuse its `_today_local()` so quest resets and streak
resets agree to the minute, including across the midnight / DST boundary.

Daily period key:  ISO date,      e.g. "2026-05-18"
Weekly period key: ISO year+week, e.g. "2026-W21"

NOTE: this module imports `apps.progress.streak_service`, which imports
`apps.progress.models`. It is therefore deliberately NOT imported from
`quests/__init__.py` (that runs during model registration, before
`progress.models` finishes importing). Import it from service/view code,
which only runs well after app load.
"""
from datetime import date

from apps.progress.streak_service import _today_local


def today_local() -> date:
    """The current Europe/Bucharest calendar date, per the streak service."""
    return _today_local()


def daily_period_key(day: date | None = None) -> str:
    """ISO date string for `day` (default: today). e.g. '2026-05-18'."""
    return (day or today_local()).isoformat()


def weekly_period_key(day: date | None = None) -> str:
    """ISO year+week string for the week containing `day` (default: today).

    Uses ISO-8601 week numbering (weeks start Monday; the ISO year can
    differ from the calendar year in late December / early January).
    e.g. '2026-W21'.
    """
    iso_year, iso_week, _ = (day or today_local()).isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def period_key_for(cadence: str, day: date | None = None) -> str:
    """Period key for `cadence` ('daily' | 'weekly') on `day`.

    Raises ValueError for an unknown cadence so a typo fails loudly
    rather than silently bucketing assignments into the wrong period.
    """
    if cadence == "daily":
        return daily_period_key(day)
    if cadence == "weekly":
        return weekly_period_key(day)
    raise ValueError(f"Unknown quest cadence: {cadence!r}")
