"""
Content API views for MathEd Romania.

These endpoints serve curriculum content to authenticated students/teachers.
All content is read-only via the API — creation/editing happens in Django admin.
"""
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.progress.unlock import get_passed_test_ids, get_unlock_map, is_lesson_unlocked

from .models import GlossaryTerm, Grade, Lesson, Unit
from .serializers import (
    GlossaryTermSerializer,
    GradeDetailSerializer,
    GradeListSerializer,
    LessonDetailSerializer,
    UnitListSerializer,
)


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

    Full grade with all published units and their lesson lists.
    Includes per-student unlock state for each lesson.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, grade_number):
        try:
            grade = Grade.objects.prefetch_related(
                "units__lessons__exercises",
                "units__lessons__test",
                "units__test",
            ).get(number=grade_number, is_active=True)
        except Grade.DoesNotExist:
            return Response(
                {"error": "Grade not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Build unlock map for all lessons in this grade
        all_lessons = Lesson.objects.filter(
            unit__grade=grade,
            is_published=True,
        ).select_related("unit__grade", "test")
        unlock_map = get_unlock_map(all_lessons, request.user)

        serializer = GradeDetailSerializer(
            grade,
            context={"unlock_map": unlock_map, "request": request},
        )
        return Response(serializer.data)


class UnitDetailView(APIView):
    """
    GET /api/v1/content/units/<unit_id>/

    Unit with all its published lessons.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, unit_id):
        try:
            unit = Unit.objects.prefetch_related(
                "lessons__exercises",
                "test",
            ).get(id=unit_id, is_published=True)
        except Unit.DoesNotExist:
            return Response(
                {"error": "Unit not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UnitListSerializer(unit)
        return Response(serializer.data)


class LessonDetailView(APIView):
    """
    GET /api/v1/content/lessons/<lesson_id>/

    Full lesson with content, exercises, and glossary terms.
    Returns 403 if the lesson is locked for this student.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lesson_id):
        try:
            lesson = Lesson.objects.select_related(
                "unit__grade",
            ).prefetch_related(
                "exercises",
                "glossary_terms",
            ).get(id=lesson_id, is_published=True)
        except Lesson.DoesNotExist:
            return Response(
                {"error": "Lesson not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Enforce unlock check
        passed_test_ids = get_passed_test_ids(request.user)
        if not is_lesson_unlocked(lesson, passed_test_ids):
            return Response(
                {"error": "Lecția nu este disponibilă încă.", "locked": True},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = LessonDetailSerializer(lesson)
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