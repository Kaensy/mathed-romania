"""
Streak service for MathEd Romania.

Public API:
    record_activity(user, activity_type) -> dict

All dates are computed in Europe/Bucharest local time.
"""
from zoneinfo import ZoneInfo

from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import Streak, StreakActivity

BUCHAREST_TZ = ZoneInfo("Europe/Bucharest")
MAX_FREEZES = 2


def _today_local():
    return timezone.now().astimezone(BUCHAREST_TZ).date()


def _idempotent_payload(streak):
    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "freeze_count": streak.freeze_count,
        "freeze_used": False,
        "freeze_earned": False,
        "is_new_activity": False,
    }


def record_activity(user, activity_type: str) -> dict:
    today = _today_local()
    freeze_used = False
    freeze_earned = False

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
                    return _idempotent_payload(streak)
                if gap == 1:
                    streak.current_streak += 1
                elif gap == 2 and streak.freeze_count > 0:
                    streak.freeze_count -= 1
                    streak.current_streak += 1
                    freeze_used = True
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
                freeze_earned = True

            streak.last_active_date = today
            streak.save()
    except IntegrityError:
        streak, _ = Streak.objects.get_or_create(student=user)
        return _idempotent_payload(streak)

    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "freeze_count": streak.freeze_count,
        "freeze_used": freeze_used,
        "freeze_earned": freeze_earned,
        "is_new_activity": True,
    }
