"""
Streak service for MathEd Romania.

Public API:
    record_activity(user, activity_type) -> int
    evaluate_streak_badges_for(user) -> list[str]

`record_activity` updates the streak counter for today and attempts the
`daily_first_login` XP grant. It returns the XP integer granted by this
call (0 on duplicate or non-student). Streak badge evaluation moved out
into `evaluate_streak_badges_for` so views can sequence it independently.

All dates are computed in Europe/Bucharest local time.
"""
import logging
from zoneinfo import ZoneInfo

from django.db import IntegrityError, transaction
from django.utils import timezone

from .badges.service import evaluate_badges_for_event
from .models import Streak, StreakActivity
from .xp import award_xp, student_grade

logger = logging.getLogger(__name__)

BUCHAREST_TZ = ZoneInfo("Europe/Bucharest")
MAX_FREEZES = 2


def _today_local():
    return timezone.now().astimezone(BUCHAREST_TZ).date()


def record_activity(user, activity_type: str) -> int:
    today = _today_local()

    try:
        with transaction.atomic():
            StreakActivity.objects.create(
                student=user, date=today, activity_type=activity_type,
            )
            Streak.objects.get_or_create(student=user)
            streak = Streak.objects.select_for_update().get(student=user)

            last = streak.last_active_date
            if last is None:
                streak.current_streak = 1
            else:
                gap = (today - last).days
                if gap <= 0:
                    return _try_daily_first_login(user, today)
                if gap == 1:
                    streak.current_streak += 1
                elif gap == 2 and streak.freeze_count > 0:
                    streak.freeze_count -= 1
                    streak.current_streak += 1
                else:
                    streak.current_streak = 1

            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak

            if (
                streak.current_streak > 0
                and streak.current_streak % 7 == 0
                and streak.freeze_count < MAX_FREEZES
            ):
                streak.freeze_count += 1

            streak.last_active_date = today
            streak.save()
    except IntegrityError:
        return _try_daily_first_login(user, today)

    return _try_daily_first_login(user, today)


def _try_daily_first_login(user, today) -> int:
    grade = student_grade(user)
    if grade is None:
        return 0
    return award_xp(
        user,
        "daily_first_login",
        {"date": today.isoformat(), "grade_id": grade.id},
        grade,
    )


def evaluate_streak_badges_for(user) -> list[str]:
    """View-side helper to evaluate streak badges after `record_activity`.

    Returns the list of newly-earned badge keys (same shape the old
    `record_activity` used to return). Swallows badge-eval errors so a
    badge bug never breaks the request.
    """
    streak = Streak.objects.filter(student=user).first()
    if streak is None:
        return []
    try:
        return evaluate_badges_for_event(user, "streak_updated", {"streak": streak})
    except Exception:
        logger.warning("Streak badge evaluation failed", exc_info=True)
        return []
