"""
Content serializers for MathEd Romania.

Hierarchy: Grade → Units → Topics → Lessons.
Topics own Exercises and Tests.
Lesson detail includes full blocks array; list view shows summary only.
"""
from rest_framework import serializers

from .models import Exercise, GlossaryTerm, Grade, Lesson, Test, Topic, Unit


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ["id", "exercise_type", "difficulty", "template"]


class GlossaryTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlossaryTerm
        fields = ["id", "term", "definition"]


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ["id", "scope", "pass_threshold", "time_limit_minutes", "composition"]


# ─── Lesson serializers ───────────────────────────────────────────────────────

class LessonListSerializer(serializers.ModelSerializer):
    """Lightweight lesson for listing inside a topic."""
    is_locked = serializers.SerializerMethodField()
    topic_id = serializers.IntegerField(source="topic.id", read_only=True)
    topic_test_id = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id", "order", "title", "summary",
            "topic_id", "topic_test_id",
            "is_locked",
        ]

    def get_is_locked(self, obj):
        unlock_map = self.context.get("unlock_map", {})
        return not unlock_map.get(obj.id, True)

    def get_topic_test_id(self, obj):
        try:
            test = obj.topic.test
            return test.id if test.is_published else None
        except Exception:
            return None


class LessonDetailSerializer(serializers.ModelSerializer):
    """Full lesson with blocks."""
    topic_id = serializers.IntegerField(source="topic.id", read_only=True)
    topic_title = serializers.CharField(source="topic.title", read_only=True)
    topic_order = serializers.IntegerField(source="topic.order", read_only=True)
    topic_test_id = serializers.SerializerMethodField()
    topic_exercise_count = serializers.SerializerMethodField()
    unit_id = serializers.IntegerField(source="topic.unit.id", read_only=True)
    unit_title = serializers.CharField(source="topic.unit.title", read_only=True)
    unit_order = serializers.IntegerField(source="topic.unit.order", read_only=True)
    grade_number = serializers.IntegerField(source="topic.unit.grade.number", read_only=True)
    prev_lesson_id = serializers.SerializerMethodField()
    next_lesson_id = serializers.SerializerMethodField()
    glossary_terms = GlossaryTermSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id", "order", "title", "summary", "blocks",
            "topic_id", "topic_title", "topic_order", "topic_test_id",
            "topic_exercise_count",
            "unit_id", "unit_title", "unit_order", "grade_number",
            "prev_lesson_id", "next_lesson_id",
            "glossary_terms",
            "updated_at",
        ]

    def get_topic_test_id(self, obj):
        try:
            test = obj.topic.test
            return test.id if test.is_published else None
        except Exception:
            return None

    def get_topic_exercise_count(self, obj):
        return obj.topic.exercises.filter(is_active=True).count()

    def get_prev_lesson_id(self, obj):
        """Previous lesson — goes across topic boundaries within the same unit."""
        # First try within same topic
        prev = (
            Lesson.objects
            .filter(topic=obj.topic, order__lt=obj.order, is_published=True)
            .order_by("-order")
            .values_list("id", flat=True)
            .first()
        )
        if prev:
            return prev

        # Try last lesson of previous topic in same unit
        prev_topic = (
            Topic.objects
            .filter(unit=obj.topic.unit, order__lt=obj.topic.order, is_published=True)
            .order_by("-order")
            .first()
        )
        if prev_topic:
            return (
                prev_topic.lessons
                .filter(is_published=True)
                .order_by("-order")
                .values_list("id", flat=True)
                .first()
            )
        return None

    def get_next_lesson_id(self, obj):
        """Next lesson — goes across topic boundaries within the same unit."""
        # First try within same topic
        next_ = (
            Lesson.objects
            .filter(topic=obj.topic, order__gt=obj.order, is_published=True)
            .order_by("order")
            .values_list("id", flat=True)
            .first()
        )
        if next_:
            return next_

        # Try first lesson of next topic in same unit
        next_topic = (
            Topic.objects
            .filter(unit=obj.topic.unit, order__gt=obj.topic.order, is_published=True)
            .order_by("order")
            .first()
        )
        if next_topic:
            return (
                next_topic.lessons
                .filter(is_published=True)
                .order_by("order")
                .values_list("id", flat=True)
                .first()
            )
        return None


# ─── Topic serializers ────────────────────────────────────────────────────────

class TopicListSerializer(serializers.ModelSerializer):
    """Topic with lesson list — used on GradePage / UnitDetailView."""
    lessons = serializers.SerializerMethodField()
    test = TestSerializer(read_only=True)
    exercise_count = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            "id", "order", "title", "description",
            "is_published", "practice_minimum",
            "exercise_count", "lessons", "test",
        ]

    def get_lessons(self, obj):
        lessons = obj.published_lessons
        return LessonListSerializer(
            lessons,
            many=True,
            context=self.context,
        ).data

    def get_exercise_count(self, obj):
        return obj.exercises.filter(is_active=True).count()


# ─── Unit serializers ─────────────────────────────────────────────────────────

class UnitListSerializer(serializers.ModelSerializer):
    """Unit with topic summaries and test info."""
    topics = serializers.SerializerMethodField()
    test = TestSerializer(read_only=True)
    topic_count = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = [
            "id", "order", "title", "description",
            "recommended_unlock_date",
            "topic_count", "topics", "test",
        ]

    def get_topics(self, obj):
        topics = obj.published_topics
        return TopicListSerializer(
            topics,
            many=True,
            context=self.context,
        ).data

    def get_topic_count(self, obj):
        return obj.topics.filter(is_published=True).count()


# ─── Grade serializers ────────────────────────────────────────────────────────

class GradeDetailSerializer(serializers.ModelSerializer):
    units = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = ["id", "number", "name", "units"]

    def get_units(self, obj):
        units = obj.published_units
        return UnitListSerializer(
            units,
            many=True,
            context=self.context,
        ).data


class GradeListSerializer(serializers.ModelSerializer):
    unit_count = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = ["id", "number", "name", "unit_count"]

    def get_unit_count(self, obj):
        return obj.units.filter(is_published=True).count()
