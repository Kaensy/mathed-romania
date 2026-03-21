"""
Unlock logic for MathEd Romania.

Hierarchy: Grade → Unit → Topic → Lesson

Rules:
  - Lesson 1 of Topic 1 of Unit 1 (of the grade) is always unlocked.
  - Within a multi-lesson topic: lessons unlock sequentially by order
    (no test gate — they're part of the same topic).
  - Topic N unlocks when the student passes Topic N-1's test.
  - First topic of Unit N+1 unlocks when the student passes Unit N's test.
  - If a topic has no published test, the next topic is always unlocked.
"""
from apps.content.models import Lesson, Topic, Unit
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
    Return True if this lesson is accessible for a student
    with the given set of passed test IDs.
    """
    topic = lesson.topic
    unit = topic.unit

    # ── Within-topic unlock ───────────────────────────────────────────────
    # Non-first lessons within a topic unlock when the previous lesson in
    # the same topic is published (no test gate within a topic).
    if lesson.order > 1:
        prev_in_topic = (
            Lesson.objects
            .filter(topic=topic, order=lesson.order - 1, is_published=True)
            .exists()
        )
        # If there's a previous lesson in the same topic, it's accessible
        # (the whole topic is either available or not — topic-level gate below)
        # We fall through to the topic-level check to determine availability.

    # ── Topic-level unlock (applies to all lessons in the topic) ─────────
    # First topic of first unit of the grade → always unlocked
    first_unit = Unit.objects.filter(
        grade=unit.grade,
        is_published=True,
    ).order_by("order").first()

    if first_unit and first_unit.id == unit.id:
        # We're in the first unit
        first_topic = Topic.objects.filter(
            unit=unit,
            is_published=True,
        ).order_by("order").first()

        if first_topic and first_topic.id == topic.id:
            return True  # First topic of first unit — always open

        # Other topics in first unit — need previous topic's test
        prev_topic = Topic.objects.filter(
            unit=unit,
            order__lt=topic.order,
            is_published=True,
        ).order_by("-order").first()

        return _topic_test_passed(prev_topic, passed_test_ids)

    # First topic of a non-first unit — need previous unit's test
    if topic.order == Topic.objects.filter(unit=unit, is_published=True).order_by("order").first().order:
        prev_unit = Unit.objects.filter(
            grade=unit.grade,
            order__lt=unit.order,
            is_published=True,
        ).order_by("-order").first()

        if not prev_unit:
            return True

        return _unit_test_passed(prev_unit, passed_test_ids)

    # Non-first topic in non-first unit — need previous topic's test
    prev_topic = Topic.objects.filter(
        unit=unit,
        order__lt=topic.order,
        is_published=True,
    ).order_by("-order").first()

    return _topic_test_passed(prev_topic, passed_test_ids)


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


def get_unlock_map(lessons, student) -> dict[int, bool]:
    """
    Given a queryset/list of lessons and a student, return a dict of
    {lesson_id: is_unlocked} for all lessons.
    """
    passed_test_ids = get_passed_test_ids(student)
    return {
        lesson.id: is_lesson_unlocked(lesson, passed_test_ids)
        for lesson in lessons
    }
