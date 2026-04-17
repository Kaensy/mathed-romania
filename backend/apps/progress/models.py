"""
Progress tracking models for MathEd Romania.
Tracks lesson completion, exercise attempts, test results,
classroom pacing, and engagement streaks.
"""
import uuid

from django.conf import settings
from django.db import models


class LessonProgress(models.Model):
    """Tracks per-student, per-lesson completion (content reading)."""

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
    # Groups all attempts from one 5-exercise practice batch together.
    session_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Groups attempts from a single practice batch",
    )
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exercise_attempts"
        ordering = ["-attempted_at"]

    def __str__(self):
        result = "✓" if self.is_correct else "✗"
        return f"{self.student.email} — {result} — {self.exercise}"


class CategoryProgress(models.Model):
    """
    Tracks per-student, per-topic, per-category tier completion.
    Tier unlock order: easy → medium/hard available → hard cleared.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="category_progress",
        limit_choices_to={"user_type": "student"},
    )
    topic = models.ForeignKey(
        "content.Topic",
        on_delete=models.CASCADE,
        related_name="category_progress",
    )
    category = models.CharField(max_length=50)
    easy_cleared = models.BooleanField(default=False)
    medium_cleared = models.BooleanField(default=False)
    hard_cleared = models.BooleanField(default=False)
    category_failure_count = models.PositiveIntegerField(
        default=0,
        help_text="First-wrong-in-batch counter per category. Resets when hint is used.",
    )
    last_failure_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of last counted failure. Used for 7-day sliding window reset.",
    )

    class Meta:
        db_table = "category_progress"
        unique_together = [("student", "topic", "category")]

    def __str__(self):
        return f"{self.student.email} — {self.topic.title} / {self.category}"


class TestAttempt(models.Model):
    """Records a student's test session. Used for both topic and unit tests."""
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        ABANDONED = "abandoned", "Abandoned"

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
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )
    exercise_instances = models.JSONField(
        default=list,
        help_text="Generated exercise instances for this attempt",
    )
    answers = models.JSONField(
        default=dict,
        help_text="Submitted answers: {index: {answer, is_correct, exercise_id}}",
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final score percentage, set on completion",
    )
    passed = models.BooleanField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "test_attempts"
        ordering = ["-started_at"]

    def __str__(self):
        result = f"{self.score}%" if self.score is not None else "in progress"
        return f"{self.student.email} — {self.test} — {result}"


class ClassroomPace(models.Model):
    """Per-teacher, per-unit unlock dates."""
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
    unlock_date = models.DateField()

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
        return f"{self.student.email} — streak: {self.current_streak}"
