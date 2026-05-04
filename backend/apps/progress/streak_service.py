"""
Streak service for MathEd Romania.

Public API:
    record_activity(user, activity_type) -> list[str]

All dates are computed in Europe/Bucharest local time.
"""
import logging
from zoneinfo import ZoneInfo

from django.db import IntegrityError, transaction
from django.utils import timezone

from .badges.service import evaluate_badges_for_event
from .models import Streak, StreakActivity

logger = logging.getLogger(__name__)

BUCHAREST_TZ = ZoneInfo("Europe/Bucharest")
MAX_FREEZES = 2


def _today_local():
    return timezone.now().astimezone(BUCHAREST_TZ).date()


def record_activity(user, activity_type: str) -> list[str]:
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
                    return _evaluate_streak_badges(user, streak)
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
        streak, _ = Streak.objects.get_or_create(student=user)
        return _evaluate_streak_badges(user, streak)

    return _evaluate_streak_badges(user, streak)


def _evaluate_streak_badges(user, streak) -> list[str]:
    try:
        return evaluate_badges_for_event(user, "streak_updated", {"streak": streak})
    except Exception:
        logger.warning("Badge evaluation failed", exc_info=True)
        return []
