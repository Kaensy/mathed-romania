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


class GlossaryUnitSerializer(serializers.ModelSerializer):
    grade_number = serializers.IntegerField(source="grade.number", read_only=True)

    class Meta:
        model = Unit
        fields = ["id", "grade_number", "order", "title"]


class GlossaryTermSerializer(serializers.ModelSerializer):
    unit = GlossaryUnitSerializer(read_only=True)

    class Meta:
        model = GlossaryTerm
        fields = ["id", "term", "aliases", "definition", "category", "examples", "unit"]


class TestSerializer(serializers.ModelSerializer):
    is_locked = serializers.SerializerMethodField()
    best_score = serializers.SerializerMethodField()
    passed = serializers.SerializerMethodField()
    attempts_count = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = [
            "id", "scope", "pass_threshold", "time_limit_minutes",
            "composition",
            "is_locked", "best_score", "passed", "attempts_count",
        ]

    def get_is_locked(self, obj):
        test_unlock_map = self.context.get("test_unlock_map", {})
        return not test_unlock_map.get(obj.id, True)

    def get_best_score(self, obj):
        info = self.context.get("test_attempt_map", {}).get(obj.id)
        return info["best_score"] if info else None

    def get_passed(self, obj):
        info = self.context.get("test_attempt_map", {}).get(obj.id)
        return info["passed"] if info else False

    def get_attempts_count(self, obj):
        info = self.context.get("test_attempt_map", {}).get(obj.id)
        return info["attempts_count"] if info else 0


# ─── Lesson serializers ───────────────────────────────────────────────────────

class LessonListSerializer(serializers.ModelSerializer):
    """Lightweight lesson for listing inside a topic."""
    is_locked = serializers.SerializerMethodField()
    progress_status = serializers.SerializerMethodField()
    mastery_tier = serializers.SerializerMethodField()
    topic_id = serializers.IntegerField(source="topic.id", read_only=True)
    topic_test_id = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id", "order", "title", "summary",
            "topic_id", "topic_test_id",
            "is_locked", "progress_status", "mastery_tier",
        ]

    def get_is_locked(self, obj):
        unlock_map = self.context.get("unlock_map", {})
        return not unlock_map.get(obj.id, True)

    def get_progress_status(self, obj):
        lesson_progress_map = self.context.get("lesson_progress_map", {})
        return lesson_progress_map.get(obj.id, "not_started")

    def get_mastery_tier(self, obj):
        mastery_map = self.context.get("topic_mastery_map", {})
        return mastery_map.get(obj.topic_id, "none")

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
    topic_test_locked = serializers.SerializerMethodField()
    topic_exercise_count = serializers.SerializerMethodField()
    unit_id = serializers.IntegerField(source="topic.unit.id", read_only=True)
    unit_title = serializers.CharField(source="topic.unit.title", read_only=True)
    unit_order = serializers.IntegerField(source="topic.unit.order", read_only=True)
    grade_number = serializers.IntegerField(source="topic.unit.grade.number", read_only=True)
    prev_lesson_id = serializers.SerializerMethodField()
    next_lesson_id = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id", "order", "title", "summary", "blocks",
            "topic_id", "topic_title", "topic_order", "topic_test_id", "topic_test_locked",
            "topic_exercise_count",
            "unit_id", "unit_title", "unit_order", "grade_number",
            "prev_lesson_id", "next_lesson_id",
            "updated_at",
        ]

    def _published_topic_test(self, obj):
        try:
            test = obj.topic.test
        except Test.DoesNotExist:
            return None
        if not test or not test.is_published:
            return None
        return test

    def get_topic_test_id(self, obj):
        test = self._published_topic_test(obj)
        return test.id if test else None

    def get_topic_test_locked(self, obj):
        test = self._published_topic_test(obj)
        if not test:
            return False
        from apps.progress.unlock import is_test_unlocked
        passed_test_ids = self.context.get("passed_test_ids")
        if passed_test_ids is None:
            from apps.progress.unlock import get_passed_test_ids
            request = self.context.get("request")
            if request is None:
                return False
            passed_test_ids = get_passed_test_ids(request.user)
        return not is_test_unlocked(test, passed_test_ids)

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
    test = serializers.SerializerMethodField()
    exercise_count = serializers.SerializerMethodField()
    has_practiced = serializers.SerializerMethodField()
    mastery_tier = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            "id", "order", "title", "description",
            "is_published", "practice_minimum",
            "exercise_count", "has_practiced", "mastery_tier",
            "lessons", "test",
        ]

    def get_mastery_tier(self, obj):
        mastery_map = self.context.get("topic_mastery_map", {})
        return mastery_map.get(obj.id, "none")

    def get_lessons(self, obj):
        lessons = obj.published_lessons
        return LessonListSerializer(
            lessons,
            many=True,
            context=self.context,
        ).data

    def get_test(self, obj):
        try:
            test = obj.test
        except Test.DoesNotExist:
            return None
        if not test or not test.is_published:
            return None
        return TestSerializer(test, context=self.context).data

    def get_exercise_count(self, obj):
        return obj.exercises.filter(is_active=True).count()

    def get_has_practiced(self, obj):
        practiced_ids = self.context.get("practiced_topic_ids", set())
        return obj.id in practiced_ids


# ─── Unit serializers ─────────────────────────────────────────────────────────

class UnitListSerializer(serializers.ModelSerializer):
    """Unit with topic summaries and test info."""
    topics = serializers.SerializerMethodField()
    test = serializers.SerializerMethodField()
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

    def get_test(self, obj):
        try:
            test = obj.test
        except Test.DoesNotExist:
            return None
        if not test or not test.is_published:
            return None
        return TestSerializer(test, context=self.context).data

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
