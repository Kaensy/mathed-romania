"""
Unlock logic for MathEd Romania.

Hierarchy: Grade → Unit → Topic → Lesson

Rules:
  - Lessons (theory) are always viewable within a unit. The only gate on
    lesson access is a cross-unit one: to view lessons in a non-first unit,
    the previous unit's test must be passed.
  - Topic tests are sequentially gated inside a unit:
      * first topic of the first unit → always unlocked
      * first topic of a non-first unit → previous unit's test must pass
      * non-first topic in any unit → previous topic's test in the same
        unit must pass
  - A unit test unlocks when the last topic of that unit has a passed test.
    If the unit has no topics with published tests, the unit test is free.
  - If a topic has no published test, it does not block the next topic
    (handled by `_topic_test_passed`). Same for unit tests.
"""
from apps.content.models import Lesson, Test, Topic, Unit
from apps.progress.models import TestAttempt


def get_passed_test_ids(student) -> set[int]:
    """Return set of test IDs the student has passed."""
    return set(
        TestAttempt.objects.filter(
            student=student,
            passed=True,
            status=TestAttempt.Status.COMPLETED,
        ).values_list("test_id", flat=True)
    )


def is_lesson_unlocked(lesson: Lesson, passed_test_ids: set[int]) -> bool:
    """
    Lessons are always viewable within a unit (theory is free).
    The only gate is cross-unit: to access any lesson in a non-first unit,
    the previous unit's test must be passed.
    """
    unit = lesson.topic.unit

    prev_unit = Unit.objects.filter(
        grade=unit.grade,
        order__lt=unit.order,
        is_published=True,
    ).order_by("-order").first()

    if not prev_unit:
        return True

    return _unit_test_passed(prev_unit, passed_test_ids)


def is_test_unlocked(test: Test, passed_test_ids: set[int]) -> bool:
    """
    Tests are sequentially gated.

    Topic test (test.scope == "topic"):
      - first topic of first unit of the grade → always unlocked
      - first topic of a non-first unit → prev unit's test must pass
      - non-first topic in any unit → prev topic's test in that unit must pass

    Unit test (test.scope == "unit"):
      - unlocked once the last topic of the unit has a passed test
      - if the unit has no published topics with tests → always unlocked
    """
    if test.scope == Test.Scope.TOPIC:
        topic = test.topic
        if topic is None:
            return False
        unit = topic.unit

        first_topic = Topic.objects.filter(
            unit=unit,
            is_published=True,
        ).order_by("order").first()
        is_first_topic = first_topic is not None and first_topic.id == topic.id

        if is_first_topic:
            prev_unit = Unit.objects.filter(
                grade=unit.grade,
                order__lt=unit.order,
                is_published=True,
            ).order_by("-order").first()

            if not prev_unit:
                return True

            return _unit_test_passed(prev_unit, passed_test_ids)

        prev_topic = Topic.objects.filter(
            unit=unit,
            order__lt=topic.order,
            is_published=True,
        ).order_by("-order").first()

        return _topic_test_passed(prev_topic, passed_test_ids)

    if test.scope == Test.Scope.UNIT:
        unit = test.unit
        if unit is None:
            return False

        last_topic = Topic.objects.filter(
            unit=unit,
            is_published=True,
        ).order_by("-order").first()

        if last_topic is None:
            return True

        return _topic_test_passed(last_topic, passed_test_ids)

    return False


def _topic_test_passed(topic, passed_test_ids: set[int]) -> bool:
    """Return True if the topic has no published test, or if its test is passed."""
    if not topic:
        return True
    try:
        test = topic.test
        if not test.is_published:
            return True
        return test.id in passed_test_ids
    except Exception:
        return True  # No test on this topic → unlocked


def _unit_test_passed(unit, passed_test_ids: set[int]) -> bool:
    """Return True if the unit has no published test, or if its test is passed."""
    if not unit:
        return True
    try:
        test = unit.test
        if not test.is_published:
            return True
        return test.id in passed_test_ids
    except Exception:
        return True


def get_unlock_map(lessons, student, passed_test_ids: set[int] | None = None) -> dict[int, bool]:
    """
    Given a queryset/list of lessons and a student, return a dict of
    {lesson_id: is_unlocked} for all lessons.

    If `passed_test_ids` is provided, it is used directly (avoids re-querying
    when the caller already has it). Otherwise it is computed from `student`.
    """
    if passed_test_ids is None:
        passed_test_ids = get_passed_test_ids(student)
    return {
        lesson.id: is_lesson_unlocked(lesson, passed_test_ids)
        for lesson in lessons
    }


def get_test_unlock_map(tests, student, passed_test_ids: set[int] | None = None) -> dict[int, bool]:
    """
    Given a queryset/list of tests and a student, return a dict of
    {test_id: is_unlocked} for all tests.

    If `passed_test_ids` is provided, it is used directly (avoids re-querying
    when the caller already has it). Otherwise it is computed from `student`.
    """
    if passed_test_ids is None:
        passed_test_ids = get_passed_test_ids(student)
    return {
        test.id: is_test_unlocked(test, passed_test_ids)
        for test in tests
    }
