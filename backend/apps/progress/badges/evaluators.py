"""
Badge predicates. Each evaluator returns True when the user qualifies for the
badge right now; awarding (insertion into the Achievement table) is handled
by service.evaluate_badges_for_event.

Evaluators are pure read functions — no DB writes — and import models lazily
to keep this module importable from anywhere in apps.progress.
"""
from collections import defaultdict


# ---------------------------------------------------------------------------
# Event: lesson_opened          context: {"lesson": Lesson}
# ---------------------------------------------------------------------------

def first_lesson_opened(user, context) -> bool:
    return True


def unit_fully_explored(user, context) -> bool:
    from apps.content.models import Lesson
    from apps.progress.models import LessonProgress

    opened_lesson_ids = set(
        LessonProgress.objects
        .filter(student=user)
        .exclude(status=LessonProgress.Status.NOT_STARTED)
        .values_list("lesson_id", flat=True)
    )
    if not opened_lesson_ids:
        return False

    lessons_by_unit: dict[int, set[int]] = defaultdict(set)
    for lesson_id, unit_id in (
        Lesson.objects.filter(is_published=True, topic__unit__is_published=True)
        .values_list("id", "topic__unit_id")
    ):
        lessons_by_unit[unit_id].add(lesson_id)

    for unit_id, lesson_ids in lessons_by_unit.items():
        if lesson_ids and lesson_ids.issubset(opened_lesson_ids):
            return True
    return False


# ---------------------------------------------------------------------------
# Event: exercise_attempted     context: {} (evaluators query directly)
# ---------------------------------------------------------------------------

def medium_tier_x5(user, context) -> bool:
    from apps.progress.models import CategoryProgress

    return (
        CategoryProgress.objects
        .filter(student=user, medium_cleared=True)
        .count() >= 5
    )


def hard_tier_x5(user, context) -> bool:
    from apps.progress.models import CategoryProgress

    return (
        CategoryProgress.objects
        .filter(student=user, hard_cleared=True)
        .count() >= 5
    )


# ---------------------------------------------------------------------------
# Event: test_finished          context: {"test_attempt": TestAttempt}
# ---------------------------------------------------------------------------

def first_topic_test_passed(user, context) -> bool:
    attempt = context["test_attempt"]
    return bool(attempt.passed) and attempt.test.scope == "topic"


def unit_1_complete(user, context) -> bool:
    from apps.content.models import Unit

    attempt = context["test_attempt"]
    if not attempt.passed or attempt.test.scope != "unit":
        return False
    unit = attempt.test.unit
    if unit is None:
        return False
    first_unit_id = (
        Unit.objects.filter(grade=unit.grade)
        .order_by("order")
        .values_list("id", flat=True)
        .first()
    )
    return unit.id == first_unit_id


def test_perfect_score(user, context) -> bool:
    attempt = context["test_attempt"]
    return attempt.score is not None and attempt.score >= 100


def _topic_mastery_for_user(user) -> dict[int, str]:
    """
    Compute the mastery tier for every topic the user has a passed topic test
    for. Mirrors _build_topic_mastery_map in apps.content.views, narrowed to
    the topics that could possibly reach stapanit/perfect.
    """
    from apps.content.models import Exercise, Test
    from apps.progress.models import CategoryProgress, TestAttempt

    passed_topic_test_ids = set(
        TestAttempt.objects
        .filter(
            student=user,
            status=TestAttempt.Status.COMPLETED,
            passed=True,
            test__scope=Test.Scope.TOPIC,
        )
        .values_list("test_id", flat=True)
    )
    if not passed_topic_test_ids:
        return {}

    test_to_topic = dict(
        Test.objects
        .filter(id__in=passed_topic_test_ids, topic__isnull=False)
        .values_list("id", "topic_id")
    )
    topic_ids = set(test_to_topic.values())
    if not topic_ids:
        return {}

    from django.db.models import Max
    best_score_by_test: dict[int, float] = {}
    for row in (
        TestAttempt.objects
        .filter(student=user, test_id__in=passed_topic_test_ids,
                status=TestAttempt.Status.COMPLETED)
        .values("test_id")
        .annotate(best=Max("score"))
    ):
        best_score_by_test[row["test_id"]] = (
            float(row["best"]) if row["best"] is not None else 0.0
        )

    topic_categories: dict[int, set[str]] = defaultdict(set)
    for row in Exercise.objects.filter(
        topic_id__in=topic_ids, is_active=True
    ).values("topic_id", "category"):
        topic_categories[row["topic_id"]].add(row["category"])

    cleared: dict[int, dict[str, set[str]]] = defaultdict(
        lambda: {"medium": set(), "hard": set()}
    )
    for row in CategoryProgress.objects.filter(
        student=user, topic_id__in=topic_ids,
    ).values("topic_id", "category", "medium_cleared", "hard_cleared"):
        if row["medium_cleared"]:
            cleared[row["topic_id"]]["medium"].add(row["category"])
        if row["hard_cleared"]:
            cleared[row["topic_id"]]["hard"].add(row["category"])

    result: dict[int, str] = {}
    for test_id, topic_id in test_to_topic.items():
        categories = topic_categories.get(topic_id, set())
        if not categories:
            continue
        if not categories.issubset(cleared[topic_id]["medium"]):
            continue
        tier = "stapanit"
        best = best_score_by_test.get(test_id, 0.0)
        if best >= 100 and categories.issubset(cleared[topic_id]["hard"]):
            tier = "perfect"
        result[topic_id] = tier
    return result


def topic_stapanit(user, context) -> bool:
    return any(
        tier in ("stapanit", "perfect")
        for tier in _topic_mastery_for_user(user).values()
    )


def topic_perfect(user, context) -> bool:
    return any(
        tier == "perfect"
        for tier in _topic_mastery_for_user(user).values()
    )


# ---------------------------------------------------------------------------
# Event: streak_updated         context: {"streak": Streak}
# ---------------------------------------------------------------------------

def streak_3(user, context) -> bool:
    return context["streak"].current_streak >= 3


def streak_7(user, context) -> bool:
    return context["streak"].current_streak >= 7


def streak_30(user, context) -> bool:
    return context["streak"].current_streak >= 30


# ---------------------------------------------------------------------------
# Event: glossary_opened        no context
# ---------------------------------------------------------------------------

def glossary_first_open(user, context) -> bool:
    return True
