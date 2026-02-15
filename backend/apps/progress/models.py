"""
Progress tracking models for MathEd Romania.
Tracks lesson completion, exercise attempts, test results,
classroom pacing, and engagement streaks.
"""
from django.conf import settings
from django.db import models


class LessonProgress(models.Model):
    """Tracks per-student, per-lesson completion."""

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progress",
        limit_choices_to={"user_type": "student"},
    )
    lesson = models.ForeignKey(
        "content.Lesson",
        on_delete=models.CASCADE,
        related_name="student_progress",
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.NOT_STARTED,
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "lesson_progress"
        unique_together = [("student", "lesson")]

    def __str__(self):
        return f"{self.student.email} — {self.lesson.title}: {self.status}"


class ExerciseAttempt(models.Model):
    """Logs every practice exercise attempt."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exercise_attempts",
        limit_choices_to={"user_type": "student"},
    )
    exercise = models.ForeignKey(
        "content.Exercise",
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    answer = models.JSONField(help_text="Student's submitted answer")
    is_correct = models.BooleanField()
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exercise_attempts"
        ordering = ["-attempted_at"]

    def __str__(self):
        result = "✓" if self.is_correct else "✗"
        return f"{self.student.email} — {result} — {self.exercise}"


class TestAttempt(models.Model):
    """Test attempt history with scores."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="test_attempts",
        limit_choices_to={"user_type": "student"},
    )
    test = models.ForeignKey(
        "content.Test",
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    score = models.DecimalField(max_digits=5, decimal_places=2)
    passed = models.BooleanField()
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "test_attempts"
        ordering = ["-started_at"]

    def __str__(self):
        result = "PASS" if self.passed else "FAIL"
        return f"{self.student.email} — {self.test} — {result} ({self.score}%)"


class ClassroomPace(models.Model):
    """
    Per-teacher, per-unit unlock dates.
    Teachers can adjust when each unit becomes available for their students.
    """

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="classroom_paces",
        limit_choices_to={"user_type": "teacher"},
    )
    unit = models.ForeignKey(
        "content.Unit",
        on_delete=models.CASCADE,
        related_name="classroom_paces",
    )
    unlock_date = models.DateField(
        help_text="Earliest date this unit unlocks for this teacher's students",
    )

    class Meta:
        db_table = "classroom_paces"
        unique_together = [("teacher", "unit")]

    def __str__(self):
        return f"{self.teacher.email} — {self.unit.title}: {self.unlock_date}"


class Streak(models.Model):
    """Daily engagement streak tracking."""

    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="streak",
        limit_choices_to={"user_type": "student"},
    )
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "streaks"

    def __str__(self):
        return f"{self.student.email} — {self.current_streak} day streak"
