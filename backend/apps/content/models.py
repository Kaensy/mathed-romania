"""
Content models for MathEd Romania.
Represents the curriculum hierarchy: Grade → Unit → Lesson → Exercise.
Tests are per-unit and gate progression to the next unit.
"""
from django.db import models


class Grade(models.Model):
    """Top-level grouping. Grades 5-8."""

    number = models.PositiveSmallIntegerField(unique=True)
    name = models.CharField(max_length=50)  # e.g., "Clasa a V-a"
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = "grades"
        ordering = ["number"]

    def __str__(self):
        return self.name

    @property
    def published_units(self):
        return self.units.filter(is_published=True)


class Unit(models.Model):
    """
    Major curriculum unit within a grade.
    e.g., "Numere Naturale", "Fractii Ordinare"
    """

    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="units")
    order = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    recommended_unlock_date = models.DateField(
        null=True,
        blank=True,
        help_text="Default earliest date this unit becomes available",
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        db_table = "units"
        ordering = ["grade", "order"]
        unique_together = [("grade", "order")]

    def __str__(self):
        return f"{self.grade.number}.{self.order} — {self.title}"

    @property
    def published_lessons(self):
        return self.lessons.filter(is_published=True)


class Lesson(models.Model):
    """
    Individual lesson within a unit.
    Contains theory, worked examples, and links to exercises.
    """

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="lessons")
    order = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200)
    summary = models.TextField(
        blank=True,
        help_text="Short description shown in lesson lists",
    )
    content = models.TextField(
        help_text="Rich text with KaTeX math notation",
    )
    is_published = models.BooleanField(default=False)
    practice_minimum = models.PositiveSmallIntegerField(
        default=5,
        help_text="Exercises to complete before next lesson unlocks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lessons"
        ordering = ["unit", "order"]
        unique_together = [("unit", "order")]

    def __str__(self):
        return f"{self.unit.grade.number}.{self.unit.order}.{self.order} — {self.title}"

    @property
    def active_exercises(self):
        return self.exercises.filter(is_active=True)


class Exercise(models.Model):
    """
    Exercise linked to a lesson. Template stored as JSONB for
    parameter randomization.
    """

    class ExerciseType(models.TextChoices):
        MULTIPLE_CHOICE = "multiple_choice", "Multiple Choice"
        FILL_BLANK = "fill_blank", "Fill in the Blank"
        EXPRESSION = "expression", "Expression Input"
        TRUE_FALSE = "true_false", "True/False"

    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="exercises")
    exercise_type = models.CharField(max_length=20, choices=ExerciseType.choices)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.MEDIUM)
    template = models.JSONField(
        help_text="JSONB template: params, answer formula, validation rules, display text",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exercises"

    def __str__(self):
        return f"Exercise ({self.exercise_type}) for {self.lesson.title}"


class Test(models.Model):
    """
    Unit evaluation test. Must be passed to unlock next unit.
    One test per unit.
    """

    unit = models.OneToOneField(Unit, on_delete=models.CASCADE, related_name="test")
    pass_threshold = models.PositiveSmallIntegerField(
        default=70,
        help_text="Minimum score (%) to pass",
    )
    time_limit_minutes = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Time limit in minutes. Null = untimed.",
    )
    exercise_count = models.PositiveSmallIntegerField(
        default=10,
        help_text="Number of exercises in this test",
    )
    retry_practice_count = models.PositiveSmallIntegerField(
        default=5,
        help_text="Extra practice exercises required after a failed attempt",
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        db_table = "tests"

    def __str__(self):
        return f"Test: {self.unit.title}"


class GlossaryTerm(models.Model):
    """
    Mathematical term definitions, cross-referenced with content.
    Searchable by students, available offline.
    """

    term = models.CharField(max_length=200)
    definition = models.TextField()
    unit = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="glossary_terms",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="glossary_terms",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "glossary_terms"
        ordering = ["term"]

    def __str__(self):
        return self.term
