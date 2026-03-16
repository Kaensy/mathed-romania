"""
Unlock logic for MathEd Romania.

Rules:
  - Lesson 1 of Unit 1 is always unlocked.
  - Lesson N unlocks when the student passes Lesson N-1's test.
  - First lesson of Unit N+1 unlocks when the student passes Unit N's test.
  - If a lesson has no test, it's always unlocked (no gate).
"""
from apps.content.models import Lesson, Unit
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


def is_lesson_unlocked(lesson, passed_test_ids: set[int]) -> bool:
    """
    Return True if this lesson is accessible for a student
    with the given set of passed test IDs.
    """
    # First lesson of first unit in the grade — always unlocked
    if lesson.order == 1:
        unit = lesson.unit
        # Check if this is the first unit in the grade
        first_unit = Unit.objects.filter(
            grade=unit.grade,
            is_published=True,
        ).order_by("order").first()

        if first_unit and first_unit.id == unit.id:
            return True  # First lesson of first unit — always open

        # First lesson of subsequent unit — need previous unit's test passed
        prev_unit = Unit.objects.filter(
            grade=unit.grade,
            order__lt=unit.order,
            is_published=True,
        ).order_by("-order").first()

        if not prev_unit:
            return True  # No previous unit found — unlock

        try:
            prev_unit_test = prev_unit.test
            if not prev_unit_test.is_published:
                return True  # Unit test not published yet — unlock
            return prev_unit_test.id in passed_test_ids
        except Exception:
            return True  # No unit test — unlock

    # Non-first lesson — need previous lesson's test passed
    prev_lesson = Lesson.objects.filter(
        unit=lesson.unit,
        order=lesson.order - 1,
        is_published=True,
    ).first()

    if not prev_lesson:
        return True  # No previous lesson found — unlock

    try:
        prev_test = prev_lesson.test
        if not prev_test.is_published:
            return True  # Previous lesson has no published test — unlock
        return prev_test.id in passed_test_ids
    except Exception:
        return True  # Previous lesson has no test — unlock


def get_unlock_map(lessons, student) -> dict[int, bool]:
    """
    Given a list of lessons and a student, return a dict of
    {lesson_id: is_unlocked} for all lessons.

    Fetches passed tests once and reuses for all lessons.
    """
    passed_test_ids = get_passed_test_ids(student)
    return {
        lesson.id: is_lesson_unlocked(lesson, passed_test_ids)
        for lesson in lessons
    }