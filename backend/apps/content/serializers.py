"""
Content serializers for MathEd Romania.

Nested serialization: Grade → Units → Lessons.
Lesson detail includes full content; list view shows summary only.
"""
from rest_framework import serializers

from .models import Exercise, GlossaryTerm, Grade, Lesson, Test, Unit


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ["id", "exercise_type", "difficulty", "template"]


class GlossaryTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlossaryTerm
        fields = ["id", "term", "definition"]


class LessonListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lesson lists — no full content."""

    exercise_count = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ["id", "order", "title", "summary", "practice_minimum", "exercise_count"]

    def get_exercise_count(self, obj):
        return obj.exercises.filter(is_active=True).count()


class LessonDetailSerializer(serializers.ModelSerializer):
    """Full lesson with content and exercises."""

    exercises = ExerciseSerializer(many=True, source="active_exercises")
    glossary_terms = GlossaryTermSerializer(many=True, read_only=True)
    unit_title = serializers.CharField(source="unit.title", read_only=True)
    grade_number = serializers.IntegerField(source="unit.grade.number", read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "order",
            "title",
            "summary",
            "content",
            "practice_minimum",
            "unit_title",
            "grade_number",
            "exercises",
            "glossary_terms",
            "updated_at",
        ]


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ["id", "pass_threshold", "time_limit_minutes", "exercise_count"]


class UnitListSerializer(serializers.ModelSerializer):
    """Unit with lesson summaries and test info."""

    lessons = LessonListSerializer(many=True, source="published_lessons")
    test = TestSerializer(read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = [
            "id",
            "order",
            "title",
            "description",
            "recommended_unlock_date",
            "lesson_count",
            "lessons",
            "test",
        ]

    def get_lesson_count(self, obj):
        return obj.lessons.filter(is_published=True).count()


class GradeDetailSerializer(serializers.ModelSerializer):
    """Grade with all its published units."""

    units = UnitListSerializer(many=True, source="published_units")

    class Meta:
        model = Grade
        fields = ["id", "number", "name", "units"]


class GradeListSerializer(serializers.ModelSerializer):
    """Lightweight grade list."""

    unit_count = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = ["id", "number", "name", "unit_count"]

    def get_unit_count(self, obj):
        return obj.units.filter(is_published=True).count()
