"""
Badge evaluation service — entry point called from views after a triggering
action (lesson opened, test submitted, streak updated, etc.).

Views are expected to wrap the call in try/except (matching the
record_activity convention in apps.progress.streak_service); this module
intentionally does not swallow exceptions.
"""
from apps.progress.models import Achievement

from . import evaluators
from .catalog import CATALOG

EVENT_EVALUATORS: dict[str, list[tuple[str, callable]]] = {
    "lesson_opened": [
        ("first_lesson_opened", evaluators.first_lesson_opened),
        ("unit_fully_explored", evaluators.unit_fully_explored),
    ],
    "exercise_attempted": [
        ("medium_tier_x5", evaluators.medium_tier_x5),
        ("hard_tier_x5", evaluators.hard_tier_x5),
    ],
    "test_finished": [
        ("first_topic_test_passed", evaluators.first_topic_test_passed),
        ("unit_1_complete", evaluators.unit_1_complete),
        ("test_perfect_score", evaluators.test_perfect_score),
        ("topic_stapanit", evaluators.topic_stapanit),
        ("topic_perfect", evaluators.topic_perfect),
    ],
    "streak_updated": [
        ("streak_3", evaluators.streak_3),
        ("streak_7", evaluators.streak_7),
        ("streak_30", evaluators.streak_30),
    ],
    "glossary_opened": [
        ("glossary_first_open", evaluators.glossary_first_open),
    ],
}


def evaluate_badges_for_event(user, event_name, context=None) -> list[str]:
    """Called from views after a triggering action. Returns the list of
    newly-earned badge keys so the caller can include them in its
    response payload (frontend pops a toast per key)."""
    evaluator_list = EVENT_EVALUATORS.get(event_name)
    if not evaluator_list:
        return []

    already_earned = set(
        Achievement.objects.filter(student=user).values_list("badge_key", flat=True)
    )
    ctx = context or {}
    newly_earned: list[str] = []

    for badge_key, fn in evaluator_list:
        if badge_key in already_earned:
            continue
        if not fn(user, ctx):
            continue
        _, created = Achievement.objects.get_or_create(
            student=user, badge_key=badge_key,
        )
        if created:
            newly_earned.append(badge_key)

    return newly_earned


def serialize_badges(keys: list[str]) -> list[dict]:
    """Enrich newly-earned keys into full dicts for the API response.
    Returns: [{key, name, description, icon_name, family, secret}, ...]
    Looks up the catalog. Skips keys not in the catalog (defensive)."""
    out: list[dict] = []
    for key in keys:
        badge = CATALOG.get(key)
        if badge is None:
            continue
        out.append({
            "key": badge.key,
            "name": badge.name,
            "description": badge.description,
            "icon_name": badge.icon_name,
            "family": badge.family,
            "secret": badge.secret,
        })
    return out
