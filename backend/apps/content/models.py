"""
Content models for MathEd Romania.

Hierarchy: Grade → Unit → Topic → Lesson
Each Topic groups one or more Lessons, and owns Exercises and a Test.
Lessons are purely content (blocks); progression gates live at the Topic level.
"""
from django.db import models


class Grade(models.Model):
    """Top-level grouping (5, 6, 7, 8)."""
    number = models.PositiveSmallIntegerField(unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "grades"
        ordering = ["number"]

    def __str__(self):
        return self.name

    @property
    def published_units(self):
        return self.units.filter(is_published=True)


class Unit(models.Model):
    """Chapter/unit within a grade. Sequential unlock between units."""
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="units")
    order = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    recommended_unlock_date = models.DateField(
        null=True,
        blank=True,
        help_text="Default earliest date this unit should unlock for students",
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        db_table = "units"
        ordering = ["grade", "order"]
        unique_together = [("grade", "order")]

    def __str__(self):
        return f"{self.grade.number}.{self.order} — {self.title}"

    @property
    def published_topics(self):
        return self.topics.filter(is_published=True)


class Topic(models.Model):
    """
    A math topic within a unit. Groups one or more Lessons.
    Owns all Exercises, one Test, and progression state.

    Single-lesson topics: one Lesson, standard flow.
    Multi-lesson topics: e.g. "Adunarea" spans two Lessons (calcul + Gauss);
      both lessons are read before practicing/testing at the topic level.
    """
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="topics")
    order = models.PositiveSmallIntegerField()
    title = models.CharField(
        max_length=200,
        help_text="Displayed on the Exerciții and Teste overview pages",
    )
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    practice_minimum = models.PositiveSmallIntegerField(
        default=5,
        help_text="Minimum exercises a student must complete before the test unlocks",
    )

    class Meta:
        db_table = "topics"
        ordering = ["unit", "order"]
        unique_together = [("unit", "order")]

    def __str__(self):
        return f"{self.unit.grade.number}.{self.unit.order}.{self.order} — {self.title}"

    @property
    def published_lessons(self):
        return self.lessons.filter(is_published=True).order_by("order")

    @property
    def active_exercises(self):
        return self.exercises.filter(is_active=True)


class Lesson(models.Model):
    """
    Individual lesson (content only) within a topic.
    Content is stored as a structured JSON array of typed blocks.
    """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="lessons")
    order = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200)
    summary = models.TextField(
        blank=True,
        help_text="Short description shown in lesson lists and cards",
    )
    blocks = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "Structured lesson content as an array of typed blocks. "
            "See BLOCK_SCHEMA.md for the full specification."
        ),
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lessons"
        ordering = ["topic", "order"]
        unique_together = [("topic", "order")]

    def __str__(self):
        unit = self.topic.unit
        return f"{unit.grade.number}.{unit.order}.{self.topic.order}.{self.order} — {self.title}"


class Exercise(models.Model):
    """
    Exercise linked to a topic. Template stored as JSONB for parameter randomization.
    """
    class ExerciseType(models.TextChoices):
        MULTIPLE_CHOICE = "multiple_choice", "Multiple Choice"
        FILL_BLANK = "fill_blank", "Fill in the Blank"
        MULTI_FILL_BLANK = "multi_fill_blank", "Multi Fill in the Blank"
        EXPRESSION = "expression", "Expression Input"
        TRUE_FALSE = "true_false", "True/False"
        DRAG_ORDER = "drag_order", "Drag to Order"
        CLICK_SELECT = "click_select", "Click to Select"
        COMPARISON = "comparison", "Comparison (<, =, >)"

    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="exercises")
    exercise_type = models.CharField(max_length=20, choices=ExerciseType.choices)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.MEDIUM)
    category = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Math exercise category e.g. 'expanded_form', 'digit_identification'",
    )
    template = models.JSONField(
        help_text="JSONB template: params, answer formula, validation rules, display text",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exercises"

    def __str__(self):
        return f"Exercise ({self.exercise_type}) — {self.topic.title} [{self.category}]"


class Test(models.Model):
    """
    Evaluation test — either a topic-level test or a unit-level test.
    Topic tests gate progression to the next topic.
    Unit tests gate progression to the next unit.
    """
    class Scope(models.TextChoices):
        TOPIC = "topic", "Topic Test"
        UNIT = "unit", "Unit Test"

    scope = models.CharField(
        max_length=10,
        choices=Scope.choices,
        default=Scope.UNIT,
    )
    unit = models.OneToOneField(
        Unit,
        on_delete=models.CASCADE,
        related_name="test",
        null=True,
        blank=True,
    )
    topic = models.OneToOneField(
        Topic,
        on_delete=models.CASCADE,
        related_name="test",
        null=True,
        blank=True,
    )
    composition = models.JSONField(
        default=list,
        help_text=(
            "List of {category, count, weight, difficulty} dicts. "
            "Example: [{\"category\": \"expanded_form\", \"count\": 2, "
            "\"weight\": 30, \"difficulty\": \"easy\"}]"
        ),
    )
    pass_threshold = models.PositiveSmallIntegerField(
        default=60,
        help_text="Minimum score (%) to pass",
    )
    time_limit_minutes = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Time limit in minutes. Null = untimed.",
    )
    retry_practice_count = models.PositiveSmallIntegerField(
        default=5,
        help_text="Extra practice exercises required after a failed attempt before retry",
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        db_table = "tests"
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(scope="topic", topic__isnull=False, unit__isnull=True) |
                    models.Q(scope="unit", unit__isnull=False, topic__isnull=True)
                ),
                name="test_scope_consistency",
            )
        ]

    def __str__(self):
        if self.scope == self.Scope.TOPIC and self.topic:
            return f"Test (Topic): {self.topic.title}"
        if self.scope == self.Scope.UNIT and self.unit:
            return f"Test (Unitate): {self.unit.title}"
        return f"Test ({self.scope})"


class GlossaryTerm(models.Model):
    """Mathematical term definitions, cross-referenced with content."""
    class Category(models.TextChoices):
        DEFINITION = "definition", "Definiție"
        NOTATION = "notation", "Notație"
        PROPERTY = "property", "Proprietate"
        OTHER = "other", "Altele"

    term = models.CharField(max_length=200, unique=True, db_index=True)
    aliases = models.JSONField(
        default=list,
        blank=True,
        help_text="Inflected forms / synonyms used for matching, e.g. [\"numere\", \"numărul\"]",
    )
    definition = models.TextField()
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="glossary_terms",
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.DEFINITION,
    )
    examples = models.JSONField(
        default=list,
        blank=True,
        help_text="Example strings; KaTeX inline $...$ allowed.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "glossary_terms"
        ordering = ["term"]

    def __str__(self):
        return self.term
