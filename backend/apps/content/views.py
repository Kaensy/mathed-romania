"""
Content API views for MathEd Romania.

These endpoints serve curriculum content to authenticated students/teachers.
All content is read-only via the API — creation/editing happens in Django admin.
"""
from collections import defaultdict

from django.db.models import Count, Max, Q

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.progress.models import (
    CategoryProgress,
    ExerciseAttempt,
    LessonProgress,
    TestAttempt,
)
from apps.progress.unlock import (
    get_passed_test_ids,
    get_test_unlock_map,
    get_unlock_map,
    is_lesson_unlocked,
)

from .models import Exercise, GlossaryTerm, Grade, Lesson, Test, Topic, Unit
from .serializers import (
    GlossaryTermSerializer,
    GradeDetailSerializer,
    GradeListSerializer,
    LessonDetailSerializer,
    UnitListSerializer,
)


def _build_progress_context(request_user, all_lessons, all_tests, topic_ids):
    """
    Build the per-student context dicts the serializers need: lesson progress,
    test unlock, best attempt stats, and whether each topic has been practiced.

    Takes pre-filtered querysets/iterables so callers can scope to a grade or
    to a single unit. Returns a dict ready to merge into serializer context.
    """
    passed_test_ids = get_passed_test_ids(request_user)

    unlock_map = get_unlock_map(all_lessons, request_user, passed_test_ids=passed_test_ids)
    test_unlock_map = get_test_unlock_map(all_tests, request_user, passed_test_ids=passed_test_ids)

    lesson_progress_map = dict(
        LessonProgress.objects.filter(
            student=request_user,
            lesson__in=all_lessons,
        ).values_list("lesson_id", "status")
    )

    test_attempt_map = {}
    for row in (
        TestAttempt.objects
        .filter(
            student=request_user,
            test__in=all_tests,
            status=TestAttempt.Status.COMPLETED,
        )
        .values("test_id")
        .annotate(
            best_score=Max("score"),
            attempts_count=Count("id"),
            passed_count=Count("id", filter=Q(passed=True)),
        )
    ):
        test_attempt_map[row["test_id"]] = {
            "best_score": float(row["best_score"]) if row["best_score"] is not None else None,
            "passed": row["passed_count"] > 0,
            "attempts_count": row["attempts_count"],
        }

    practiced_topic_ids = set(
        ExerciseAttempt.objects
        .filter(student=request_user, exercise__topic_id__in=topic_ids)
        .values_list("exercise__topic_id", flat=True)
        .distinct()
    )

    topic_mastery_map = _build_topic_mastery_map(
        request_user=request_user,
        topic_ids=topic_ids,
        all_lessons=all_lessons,
        all_tests=all_tests,
        lesson_progress_map=lesson_progress_map,
        test_attempt_map=test_attempt_map,
    )

    return {
        "unlock_map": unlock_map,
        "lesson_progress_map": lesson_progress_map,
        "test_unlock_map": test_unlock_map,
        "test_attempt_map": test_attempt_map,
        "practiced_topic_ids": practiced_topic_ids,
        "topic_mastery_map": topic_mastery_map,
    }


def _build_topic_mastery_map(
    *,
    request_user,
    topic_ids,
    all_lessons,
    all_tests,
    lesson_progress_map,
    test_attempt_map,
):
    """
    Tier per topic (highest applicable wins):
      none       — nothing opened
      deschisa   — at least one lesson in the topic has progress
      promovat   — topic test passed
      stapanit   — promovat AND every active category is medium_cleared
      perfect    — best score == 100 AND every active category is hard_cleared
    """
    topic_id_set = set(topic_ids)

    # lesson_id -> topic_id for lessons in scope
    lesson_to_topic = {
        lesson.id: lesson.topic_id
        for lesson in all_lessons
        if lesson.topic_id in topic_id_set
    }

    opened_topic_ids = {
        lesson_to_topic[lid]
        for lid, status_value in lesson_progress_map.items()
        if lid in lesson_to_topic and status_value != LessonProgress.Status.NOT_STARTED
    }

    # topic_id -> Test (topic-scoped, published)
    topic_to_test = {
        t.topic_id: t
        for t in all_tests
        if t.scope == Test.Scope.TOPIC and t.topic_id is not None
    }

    # topic_id -> set of active categories
    topic_categories: dict[int, set[str]] = defaultdict(set)
    for row in Exercise.objects.filter(
        topic_id__in=topic_id_set, is_active=True
    ).values("topic_id", "category"):
        topic_categories[row["topic_id"]].add(row["category"])

    # topic_id -> {"medium": set(categories), "hard": set(categories)}
    cleared: dict[int, dict[str, set[str]]] = defaultdict(
        lambda: {"medium": set(), "hard": set()}
    )
    for row in CategoryProgress.objects.filter(
        student=request_user, topic_id__in=topic_id_set,
    ).values("topic_id", "category", "medium_cleared", "hard_cleared"):
        if row["medium_cleared"]:
            cleared[row["topic_id"]]["medium"].add(row["category"])
        if row["hard_cleared"]:
            cleared[row["topic_id"]]["hard"].add(row["category"])

    result: dict[int, str] = {}
    for topic_id in topic_id_set:
        tier = "none"
        if topic_id in opened_topic_ids:
            tier = "deschisa"

        test = topic_to_test.get(topic_id)
        attempt = test_attempt_map.get(test.id) if test else None
        if attempt and attempt["passed"]:
            tier = "promovat"
            categories = topic_categories.get(topic_id, set())
            if categories:
                medium_cleared = cleared[topic_id]["medium"]
                if categories.issubset(medium_cleared):
                    tier = "stapanit"
                    hard_cleared = cleared[topic_id]["hard"]
                    best = attempt["best_score"]
                    if best is not None and best >= 100 and categories.issubset(hard_cleared):
                        tier = "perfect"

        result[topic_id] = tier
    return result


class GradeListView(APIView):
    """
    GET /api/v1/content/grades/

    List all active grades with unit counts.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        grades = Grade.objects.filter(is_active=True)
        serializer = GradeListSerializer(grades, many=True)
        return Response(serializer.data)


class GradeDetailView(APIView):
    """
    GET /api/v1/content/grades/<grade_number>/

    Full grade with all published units → topics → lessons.
    Includes per-student unlock state for each lesson.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, grade_number):
        try:
            grade = Grade.objects.prefetch_related(
                "units__topics__lessons",
                "units__topics__exercises",
                "units__topics__test",
                "units__test",
            ).get(number=grade_number, is_active=True)
        except Grade.DoesNotExist:
            return Response({"error": "Grade not found."}, status=status.HTTP_404_NOT_FOUND)

        # Build unlock map for all published lessons in this grade
        all_lessons = Lesson.objects.filter(
            topic__unit__grade=grade,
            is_published=True,
        ).select_related("topic__unit__grade")

        all_tests = Test.objects.filter(
            Q(topic__unit__grade=grade, scope=Test.Scope.TOPIC) |
            Q(unit__grade=grade, scope=Test.Scope.UNIT),
            is_published=True,
        )

        topic_ids = list(
            Topic.objects.filter(unit__grade=grade, is_published=True)
            .values_list("id", flat=True)
        )

        ctx = _build_progress_context(request.user, all_lessons, all_tests, topic_ids)
        ctx["request"] = request

        serializer = GradeDetailSerializer(grade, context=ctx)
        return Response(serializer.data)


class UnitDetailView(APIView):
    """
    GET /api/v1/content/units/<unit_id>/

    Unit with all its published topics and their lessons.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, unit_id):
        try:
            unit = Unit.objects.prefetch_related(
                "topics__lessons",
                "topics__exercises",
                "topics__test",
                "test",
            ).get(id=unit_id, is_published=True)
        except Unit.DoesNotExist:
            return Response({"error": "Unit not found."}, status=status.HTTP_404_NOT_FOUND)

        # Build unlock map for lessons in this unit
        all_lessons = Lesson.objects.filter(
            topic__unit=unit,
            is_published=True,
        ).select_related("topic__unit__grade")

        all_tests = Test.objects.filter(
            Q(topic__unit=unit, scope=Test.Scope.TOPIC) |
            Q(unit=unit, scope=Test.Scope.UNIT),
            is_published=True,
        )

        topic_ids = list(
            Topic.objects.filter(unit=unit, is_published=True)
            .values_list("id", flat=True)
        )

        ctx = _build_progress_context(request.user, all_lessons, all_tests, topic_ids)
        ctx["request"] = request

        serializer = UnitListSerializer(unit, context=ctx)
        return Response(serializer.data)


class LessonDetailView(APIView):
    """
    GET /api/v1/content/lessons/<lesson_id>/

    Full lesson with content blocks and glossary terms.
    Returns 403 if the lesson is locked for this student.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lesson_id):
        try:
            lesson = Lesson.objects.select_related(
                "topic__unit__grade",
            ).prefetch_related(
                "glossary_terms",
            ).get(id=lesson_id, is_published=True)
        except Lesson.DoesNotExist:
            return Response({"error": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)

        # Enforce unlock check (cross-unit gate only, now that topics are free)
        passed_test_ids = get_passed_test_ids(request.user)
        if not is_lesson_unlocked(lesson, passed_test_ids):
            return Response(
                {"error": "Lecția nu este disponibilă încă.", "locked": True},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = LessonDetailSerializer(
            lesson,
            context={
                "request": request,
                "passed_test_ids": passed_test_ids,
            },
        )
        return Response(serializer.data)


class GlossaryListView(APIView):
    """
    GET /api/v1/content/glossary/
    GET /api/v1/content/glossary/?unit=<unit_id>
    GET /api/v1/content/glossary/?search=<query>

    Searchable glossary of mathematical terms.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        terms = GlossaryTerm.objects.all()

        unit_id = request.query_params.get("unit")
        if unit_id:
            terms = terms.filter(unit_id=unit_id)

        search = request.query_params.get("search")
        if search:
            terms = terms.filter(term__icontains=search)

        serializer = GlossaryTermSerializer(terms, many=True)
        return Response(serializer.data)
