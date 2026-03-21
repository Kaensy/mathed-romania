"""
Progress API views for MathEd Romania.

Endpoints:
  POST /api/v1/progress/lessons/<id>/open/       — mark lesson in_progress
  POST /api/v1/progress/lessons/<id>/complete/   — mark lesson completed
  GET  /api/v1/progress/lessons/<id>/practice/   — get randomized exercise set
  GET  /api/v1/progress/lessons/<id>/categories/ — category list with tier states
  POST /api/v1/progress/exercises/attempt/       — submit & grade an attempt
  GET  /api/v1/progress/dashboard/               — student dashboard stats
"""
import uuid
from collections import defaultdict

from django.core import signing
from django.db.models import Case, Count, IntegerField, When
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Exercise, Lesson
from apps.progress.exercise_engine import decode_instance_token, generate_instance
from apps.progress.grading import grade_attempt
from apps.progress.models import (
    CategoryProgress,
    ExerciseAttempt,
    LessonProgress,
    TestAttempt,
)
from apps.progress.serializers import AttemptSubmitSerializer, DashboardSerializer


# ─── Lesson open ──────────────────────────────────────────────────────────────

class LessonOpenView(APIView):
    """
    POST /api/v1/progress/lessons/<lesson_id>/open/

    Called when a student opens a lesson. Creates or updates a
    LessonProgress row with status=in_progress.
    Idempotent — calling it twice on a completed lesson does nothing.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id, is_published=True)
        except Lesson.DoesNotExist:
            return Response({"error": "Lecția nu există."}, status=status.HTTP_404_NOT_FOUND)

        progress, created = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson,
            defaults={"status": LessonProgress.Status.IN_PROGRESS},
        )

        # Don't downgrade a completed lesson back to in_progress
        if not created and progress.status == LessonProgress.Status.NOT_STARTED:
            progress.status = LessonProgress.Status.IN_PROGRESS
            progress.save(update_fields=["status"])

        return Response({
            "lesson_id": lesson_id,
            "status": progress.status,
        })


# ─── Lesson complete ──────────────────────────────────────────────────────────

class LessonCompleteView(APIView):
    """
    POST /api/v1/progress/lessons/<lesson_id>/complete/

    Body (optional):
      { "time_spent_seconds": 240 }

    Marks the lesson as completed. Only succeeds if the student has met
    the practice minimum for this lesson.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id, is_published=True)
        except Lesson.DoesNotExist:
            return Response({"error": "Lecția nu există."}, status=status.HTTP_404_NOT_FOUND)

        # Count distinct exercises answered correctly for this lesson
        correct_count = ExerciseAttempt.objects.filter(
            student=request.user,
            exercise__lesson=lesson,
            is_correct=True,
        ).values("exercise_id").distinct().count()

        if correct_count < lesson.practice_minimum:
            return Response(
                {
                    "error": "practice_minimum_not_met",
                    "message": (
                        f"Trebuie să rezolvi corect cel puțin "
                        f"{lesson.practice_minimum} exerciții înainte de a finaliza lecția."
                    ),
                    "correct_count": correct_count,
                    "required": lesson.practice_minimum,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        time_spent = request.data.get("time_spent_seconds", 0)

        progress, _ = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson,
        )
        if progress.status != LessonProgress.Status.COMPLETED:
            progress.status = LessonProgress.Status.COMPLETED
            progress.completed_at = timezone.now()
            progress.time_spent_seconds = time_spent
            progress.save(update_fields=["status", "completed_at", "time_spent_seconds"])

        return Response({
            "lesson_id": lesson_id,
            "status": progress.status,
            "completed_at": progress.completed_at,
        })


# ─── Practice session ─────────────────────────────────────────────────────────

class LessonPracticeView(APIView):
    """
    GET /api/v1/progress/lessons/<lesson_id>/practice/
        ?count=5
        &category=expanded_form   (optional — empty string = uncategorized)
        &difficulty=easy          (optional — easy | medium | hard)

    Returns a randomized batch of exercise instances for practice.
    A fresh session_id UUID is generated for each request; the frontend
    must include it in every subsequent attempt submission so the backend
    can detect perfect batches.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lesson_id):
        try:
            lesson = Lesson.objects.prefetch_related("exercises").get(
                id=lesson_id, is_published=True
            )
        except Lesson.DoesNotExist:
            return Response({"error": "Lecția nu există."}, status=status.HTTP_404_NOT_FOUND)

        category = request.query_params.get("category", None)
        difficulty = request.query_params.get("difficulty", None)

        qs = lesson.exercises.filter(is_active=True)
        if category is not None:
            qs = qs.filter(category=category)
        if difficulty is not None:
            qs = qs.filter(difficulty=difficulty)

        exercises = list(qs)
        if not exercises:
            return Response(
                {"error": "Această lecție nu are exerciții active pentru filtrele selectate."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            count = min(int(request.query_params.get("count", 5)), 20)
        except (ValueError, TypeError):
            count = 5

        import random
        selected = random.sample(exercises, count) if len(exercises) >= count else random.choices(exercises, k=count)

        instances = []
        for exercise in selected:
            try:
                instances.append(generate_instance(exercise))
            except Exception:
                continue

        # One session_id per batch — ties all 5 attempts together for
        # perfect-batch detection in ExerciseAttemptView.
        session_id = str(uuid.uuid4())

        return Response({
            "lesson_id": lesson_id,
            "session_id": session_id,
            "exercises": instances,
            "practice_minimum": lesson.practice_minimum,
        })


# ─── Attempt submission ───────────────────────────────────────────────────────

class ExerciseAttemptView(APIView):
    """
    POST /api/v1/progress/exercises/attempt/

    Body:
      {
        "exercise_id":    42,
        "instance_token": "<signed token>",
        "answer":         "936",
        "session_id":     "uuid-string"   // from /practice/ response
      }

    Response:
      {
        "is_correct":       true,
        "correct_answer":   null,         // non-null only when wrong
        "tier_cleared":     "easy",       // non-null when a tier was just completed
        "error":            null
      }

    After persisting, checks whether this session is now a perfect batch
    (all 5 attempts correct) and updates CategoryProgress accordingly.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AttemptSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        exercise_id = data["exercise_id"]
        instance_token = data["instance_token"]
        student_answer = data["answer"]
        session_id = data.get("session_id")

        try:
            exercise = Exercise.objects.select_related("lesson").get(id=exercise_id, is_active=True)
        except Exercise.DoesNotExist:
            return Response({"error": "Exercițiul nu există."}, status=status.HTTP_404_NOT_FOUND)

        try:
            token_data = decode_instance_token(instance_token)
        except signing.BadSignature:
            return Response(
                {"error": "Token invalid sau expirat. Reîncarcă exercițiul."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if token_data["exercise_id"] != exercise_id:
            return Response(
                {"error": "Token nepotrivit cu exercițiul."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        exercise_type = token_data["exercise_type"]
        grading_data = token_data["grading_data"]
        is_correct, error_msg = grade_attempt(exercise_type, student_answer, grading_data)

        is_preview = request.query_params.get("preview") == "true"

        if not is_preview:
            ExerciseAttempt.objects.create(
                student=request.user,
                exercise=exercise,
                answer={"raw": student_answer},
                is_correct=is_correct,
                session_id=session_id,
            )

        # ── Perfect batch detection ────────────────────────────────────────
        tier_cleared = None
        if not is_preview and session_id:
            tier_cleared = self._check_and_update_tier(request.user, exercise, session_id)

        correct_answer_display = _build_correct_display(exercise_type, grading_data)

        return Response({
            "is_correct": is_correct,
            "correct_answer": correct_answer_display if not is_correct else None,
            "tier_cleared": tier_cleared,
            "error": error_msg,
        })

    @staticmethod
    def _check_and_update_tier(user, exercise, session_id) -> str | None:
        """
        After each attempt, check whether the batch is complete (5 attempts)
        and perfect (all correct). If so, mark the appropriate difficulty tier
        on CategoryProgress and return the tier name; else return None.
        """
        batch = ExerciseAttempt.objects.filter(student=user, session_id=session_id)
        batch_count = batch.count()

        if batch_count != 5:
            return None

        if batch.filter(is_correct=False).exists():
            return None  # Not a perfect batch

        difficulty = exercise.difficulty   # all exercises in a filtered batch share difficulty
        category = exercise.category
        lesson = exercise.lesson

        cp, _ = CategoryProgress.objects.get_or_create(
            student=user,
            lesson=lesson,
            category=category,
        )

        if difficulty == "easy" and not cp.easy_cleared:
            cp.easy_cleared = True
            cp.save(update_fields=["easy_cleared"])
            return "easy"
        elif difficulty == "medium" and not cp.medium_cleared:
            cp.medium_cleared = True
            cp.save(update_fields=["medium_cleared"])
            return "medium"
        elif difficulty == "hard" and not cp.hard_cleared:
            # Hard also satisfies medium completion (New Game+ logic)
            cp.hard_cleared = True
            if not cp.medium_cleared:
                cp.medium_cleared = True
                cp.save(update_fields=["hard_cleared", "medium_cleared"])
            else:
                cp.save(update_fields=["hard_cleared"])
            return "hard"

        return None  # Tier was already cleared — still a perfect batch, just no new unlock


# ─── Category list with tier states ──────────────────────────────────────────

class LessonCategoriesView(APIView):
    """
    GET /api/v1/progress/lessons/<lesson_id>/categories/

    Returns all exercise categories for a lesson with:
      - exercises_attempted: total attempt count for the category
      - perfect_batches:     number of 5/5 sessions the student has achieved
      - tiers:               available/cleared state for easy/medium/hard
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id, is_published=True)
        except Lesson.DoesNotExist:
            return Response({"error": "Lecția nu există."}, status=status.HTTP_404_NOT_FOUND)

        exercises = Exercise.objects.filter(lesson=lesson, is_active=True)

        # Group exercise IDs by category
        category_map: dict[str, list[int]] = {}
        for ex in exercises:
            cat = ex.category or ""
            category_map.setdefault(cat, []).append(ex.id)

        if not category_map:
            return Response({
                "lesson_id": lesson_id,
                "lesson_title": lesson.title,
                "categories": [],
            })

        # ── Attempt counts per category ────────────────────────────────────
        cat_total: dict[str, int] = defaultdict(int)
        for attempt in ExerciseAttempt.objects.filter(
            student=request.user,
            exercise__lesson=lesson,
        ).values("exercise__category"):
            cat_total[attempt["exercise__category"] or ""] += 1

        # ── Perfect batch counts per category ──────────────────────────────
        # A perfect batch = a session_id group where count=5 and all correct.
        cat_perfect: dict[str, int] = defaultdict(int)
        for cat, ex_ids in category_map.items():
            cat_perfect[cat] = (
                ExerciseAttempt.objects
                .filter(student=request.user, exercise_id__in=ex_ids, session_id__isnull=False)
                .values("session_id")
                .annotate(
                    total=Count("id"),
                    correct=Count(Case(When(is_correct=True, then=1), output_field=IntegerField())),
                )
                .filter(total=5, correct=5)
                .count()
            )

        # ── CategoryProgress tier states ───────────────────────────────────
        cp_map: dict[str, CategoryProgress] = {
            cp.category: cp
            for cp in CategoryProgress.objects.filter(student=request.user, lesson=lesson)
        }

        # ── Build response ─────────────────────────────────────────────────
        categories = []
        for cat, ex_ids in category_map.items():
            label = cat if cat else "Toate exercițiile"
            cp = cp_map.get(cat)

            easy_cleared = cp.easy_cleared if cp else False
            medium_cleared = cp.medium_cleared if cp else False
            hard_cleared = cp.hard_cleared if cp else False

            categories.append({
                "category": cat,
                "label": label,
                "exercise_count": len(ex_ids),
                "exercises_attempted": cat_total[cat],
                "perfect_batches": cat_perfect[cat],
                "tiers": {
                    "easy":   {"available": True,         "cleared": easy_cleared},
                    "medium": {"available": easy_cleared, "cleared": medium_cleared},
                    "hard":   {"available": easy_cleared, "cleared": hard_cleared},
                },
            })

        # Uncategorized last, then alphabetical
        categories.sort(key=lambda c: ("zzz" if not c["category"] else "", c["label"]))

        return Response({
            "lesson_id": lesson_id,
            "lesson_title": lesson.title,
            "categories": categories,
        })


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardView(APIView):
    """
    GET /api/v1/progress/dashboard/

    Returns aggregated stats for the authenticated student's dashboard:
      - Lesson completion counts (overall + per-unit)
      - exercises_attempted: total practice attempts ever
      - perfect_batches:     total 5/5 sessions ever
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.content.models import Unit

        user = request.user

        all_lessons = Lesson.objects.filter(is_published=True).select_related("unit__grade")
        progress_map = {
            p.lesson_id: p.status
            for p in LessonProgress.objects.filter(student=user)
        }

        total_lessons = all_lessons.count()
        completed = sum(1 for l in all_lessons if progress_map.get(l.id) == LessonProgress.Status.COMPLETED)
        in_progress = sum(1 for l in all_lessons if progress_map.get(l.id) == LessonProgress.Status.IN_PROGRESS)

        # ── Exercise stats ─────────────────────────────────────────────────
        exercises_attempted = ExerciseAttempt.objects.filter(student=user).count()

        perfect_batches = (
            ExerciseAttempt.objects
            .filter(student=user, session_id__isnull=False)
            .values("session_id")
            .annotate(
                total=Count("id"),
                correct=Count(Case(When(is_correct=True, then=1), output_field=IntegerField())),
            )
            .filter(total=5, correct=5)
            .count()
        )

        # ── Per-unit breakdown ─────────────────────────────────────────────
        units_data = []
        for unit in (
            Unit.objects.filter(is_published=True)
            .prefetch_related("lessons", "grade")
            .order_by("grade__number", "order")
        ):
            unit_lessons = [l for l in all_lessons if l.unit_id == unit.id]
            unit_completed = sum(
                1 for l in unit_lessons
                if progress_map.get(l.id) == LessonProgress.Status.COMPLETED
            )
            units_data.append({
                "unit_id": unit.id,
                "unit_title": unit.title,
                "grade_number": unit.grade.number,
                "total_lessons": len(unit_lessons),
                "completed_lessons": unit_completed,
            })

        return Response({
            "total_lessons": total_lessons,
            "completed_lessons": completed,
            "in_progress_lessons": in_progress,
            "exercises_attempted": exercises_attempted,
            "perfect_batches": perfect_batches,
            "units": units_data,
        })


# ─── Test session ─────────────────────────────────────────────────────────────

from apps.content.models import Test
from apps.progress.test_engine import build_test_session, calculate_score


class TestStartView(APIView):
    """
    POST /api/v1/progress/tests/<test_id>/start/

    Creates a new TestAttempt and generates exercise instances.
    If an in-progress attempt already exists, returns that instead
    (student can resume).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, test_id):
        try:
            test = Test.objects.get(id=test_id, is_published=True)
        except Test.DoesNotExist:
            return Response({"error": "Testul nu există."}, status=status.HTTP_404_NOT_FOUND)

        existing = TestAttempt.objects.filter(
            student=request.user,
            test=test,
            status=TestAttempt.Status.IN_PROGRESS,
        ).first()
        if existing:
            return Response({
                "attempt_id": existing.id,
                "exercises": existing.exercise_instances,
                "answers": existing.answers,
                "resumed": True,
            })

        instances = build_test_session(test)
        if not instances:
            return Response(
                {"error": "Testul nu are exerciții configurate."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        attempt = TestAttempt.objects.create(
            student=request.user,
            test=test,
            status=TestAttempt.Status.IN_PROGRESS,
            exercise_instances=instances,
            answers={},
        )

        return Response({
            "attempt_id": attempt.id,
            "exercises": instances,
            "answers": {},
            "resumed": False,
        })


class TestAnswerView(APIView):
    """
    POST /api/v1/progress/tests/<test_id>/answer/

    Body:
      {
        "attempt_id":     1,
        "index":          0,
        "instance_token": "...",
        "answer":         "936"
      }

    Grades a single answer and stores it in the attempt.
    Does not reveal correctness until test is finished.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, test_id):
        attempt_id = request.data.get("attempt_id")
        index = request.data.get("index")
        instance_token = request.data.get("instance_token")
        student_answer = request.data.get("answer")

        if any(v is None for v in [attempt_id, index, instance_token, student_answer]):
            return Response({"error": "Câmpuri lipsă."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            attempt = TestAttempt.objects.get(
                id=attempt_id,
                student=request.user,
                status=TestAttempt.Status.IN_PROGRESS,
            )
        except TestAttempt.DoesNotExist:
            return Response({"error": "Sesiune invalidă."}, status=status.HTTP_404_NOT_FOUND)

        try:
            token_data = decode_instance_token(instance_token)
        except signing.BadSignature:
            return Response({"error": "Token invalid."}, status=status.HTTP_400_BAD_REQUEST)

        exercise_type = token_data["exercise_type"]
        grading_data = token_data["grading_data"]
        is_correct, _ = grade_attempt(exercise_type, student_answer, grading_data)

        instances = attempt.exercise_instances
        weight = instances[int(index)].get("weight", 10) if int(index) < len(instances) else 10

        answers = attempt.answers
        answers[str(index)] = {
            "answer": student_answer,
            "is_correct": is_correct,
            "exercise_id": token_data.get("exercise_id"),
            "weight": weight,
        }
        attempt.answers = answers
        attempt.save(update_fields=["answers"])

        return Response({"received": True, "index": index})


class TestFinishView(APIView):
    """
    POST /api/v1/progress/tests/<test_id>/finish/

    Body: { "attempt_id": 1 }

    Finalizes the attempt, calculates score, sets passed flag.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, test_id):
        attempt_id = request.data.get("attempt_id")
        try:
            attempt = TestAttempt.objects.select_related("test").get(
                id=attempt_id,
                student=request.user,
                status=TestAttempt.Status.IN_PROGRESS,
            )
        except TestAttempt.DoesNotExist:
            return Response({"error": "Sesiune invalidă."}, status=status.HTTP_404_NOT_FOUND)

        score, _ = calculate_score(attempt.test.composition, attempt.answers)
        passed = score >= attempt.test.pass_threshold

        attempt.score = score
        attempt.passed = passed
        attempt.status = TestAttempt.Status.COMPLETED
        attempt.finished_at = timezone.now()
        attempt.save(update_fields=["score", "passed", "status", "finished_at"])

        return Response({
            "score": score,
            "passed": passed,
            "pass_threshold": attempt.test.pass_threshold,
            "answers": attempt.answers,
        })


class TestResultView(APIView):
    """
    GET /api/v1/progress/tests/<test_id>/result/

    Returns the most recent completed attempt for this student.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, test_id):
        attempt = TestAttempt.objects.filter(
            student=request.user,
            test_id=test_id,
            status=TestAttempt.Status.COMPLETED,
        ).order_by("-finished_at").first()

        if not attempt:
            return Response(
                {"error": "Niciun test completat găsit."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({
            "score": attempt.score,
            "passed": attempt.passed,
            "pass_threshold": attempt.test.pass_threshold,
            "finished_at": attempt.finished_at,
            "answers": attempt.answers,
            "exercise_instances": attempt.exercise_instances,
        })


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _build_correct_display(exercise_type: str, grading_data: dict) -> str:
    """Build a human-readable correct-answer string to show after a wrong attempt."""
    if exercise_type == "multi_fill_blank":
        parts = [f"{k} = {v}" for k, v in grading_data.get("correct_map", {}).items()]
        return ", ".join(parts)
    elif exercise_type == "fill_blank":
        # Set-membership grading
        if "valid_set" in grading_data:
            if grading_data.get("answer_display"):
                return grading_data["answer_display"]
            valid = grading_data["valid_set"]
            return f"orice număr din intervalul [{min(valid)}, {max(valid)}]"
        # Standard symbolic grading
        expr = grading_data.get("correct_expr", "")
        try:
            from apps.progress.grading import TRANSFORMATIONS, normalize
            from sympy.parsing.sympy_parser import parse_expr
            return str(parse_expr(normalize(expr), transformations=TRANSFORMATIONS))
        except Exception:  # noqa: BLE001
            return expr
    elif exercise_type == "comparison":
        left = grading_data.get("left_expr", "")
        right = grading_data.get("right_expr", "")
        try:
            import sympy
            from sympy.parsing.sympy_parser import (
                convert_xor,
                implicit_multiplication_application,
                parse_expr,
                standard_transformations,
            )
            transforms = standard_transformations + (
                implicit_multiplication_application,
                convert_xor,
            )
            l_val = parse_expr(left.replace(":", "/"), transformations=transforms)
            r_val = parse_expr(right.replace(":", "/"), transformations=transforms)
            diff = sympy.simplify(l_val - r_val)
            if diff == sympy.Integer(0):
                return "="
            return ">" if diff > 0 else "<"
        except Exception:  # noqa: BLE001
            return "?"
    elif exercise_type == "multiple_choice":
        return str(grading_data.get("correct_option_id", ""))
    elif exercise_type == "drag_order":
        return ", ".join(str(x) for x in grading_data.get("correct_order", []))
    return ""


# ─── Exercises overview ───────────────────────────────────────────────────────

class ExercisesOverviewView(APIView):
    """
    GET /api/v1/progress/exercises-overview/

    Returns all published lessons that have at least one active exercise,
    ordered by unit then lesson, with per-lesson aggregate progress for
    the authenticated student.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from collections import defaultdict
        from django.db.models import Count, Q

        user = request.user

        # All published lessons with at least one active exercise
        lessons = (
            Lesson.objects
            .filter(is_published=True, exercises__is_active=True)
            .distinct()
            .select_related("unit__grade")
            .order_by("unit__order", "order")
        )
        lesson_ids = [l.id for l in lessons]

        # Total distinct exercise categories per lesson
        cat_counts = (
            Exercise.objects
            .filter(lesson_id__in=lesson_ids, is_active=True)
            .values("lesson_id")
            .annotate(total=Count("category", distinct=True))
        )
        cat_count_map = {row["lesson_id"]: row["total"] for row in cat_counts}

        # Student's CategoryProgress — completed = medium_cleared OR hard_cleared
        completed_by_lesson: dict[int, int] = defaultdict(int)
        for cp in CategoryProgress.objects.filter(student=user, lesson_id__in=lesson_ids):
            if cp.medium_cleared or cp.hard_cleared:
                completed_by_lesson[cp.lesson_id] += 1

        # Exercises attempted per lesson
        attempt_count_map: dict[int, int] = {}
        for row in (
            ExerciseAttempt.objects
            .filter(student=user, exercise__lesson_id__in=lesson_ids)
            .values("exercise__lesson_id")
            .annotate(count=Count("id"))
        ):
            attempt_count_map[row["exercise__lesson_id"]] = row["count"]

        results = [
            {
                "lesson_id": lesson.id,
                "lesson_title": lesson.title,
                "unit_id": lesson.unit_id,
                "unit_title": lesson.unit.title,
                "unit_order": lesson.unit.order,
                "lesson_order": lesson.order,
                "total_categories": cat_count_map.get(lesson.id, 0),
                "completed_categories": completed_by_lesson.get(lesson.id, 0),
                "exercises_attempted": attempt_count_map.get(lesson.id, 0),
            }
            for lesson in lessons
        ]

        return Response({"lessons": results})


# ─── Tests overview ───────────────────────────────────────────────────────────

class TestsOverviewView(APIView):
    """
    GET /api/v1/progress/tests-overview/

    Returns all published lesson tests (scope=lesson) ordered by lesson
    sequence, with the authenticated student's best attempt status.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.db.models import Count, Max, Q

        user = request.user

        tests = (
            Test.objects
            .filter(scope=Test.Scope.LESSON, is_published=True, lesson__is_published=True)
            .select_related("lesson__unit__grade")
            .order_by("lesson__unit__order", "lesson__order")
        )
        test_ids = [t.id for t in tests]

        # Best attempt per test: passed (any) → score → most recent
        attempt_stats = (
            TestAttempt.objects
            .filter(
                student=user,
                test_id__in=test_ids,
                status=TestAttempt.Status.COMPLETED,
            )
            .values("test_id")
            .annotate(
                attempts_count=Count("id"),
                passed_count=Count("id", filter=models.Q(passed=True)),
                best_score=models.Max("score"),
            )
        )
        attempt_map = {row["test_id"]: row for row in attempt_stats}

        results = []
        for test in tests:
            a = attempt_map.get(test.id)
            results.append({
                "test_id": test.id,
                "lesson_id": test.lesson_id,
                "lesson_title": test.lesson.title,
                "unit_id": test.lesson.unit_id,
                "unit_title": test.lesson.unit.title,
                "unit_order": test.lesson.unit.order,
                "lesson_order": test.lesson.order,
                "pass_threshold": test.pass_threshold,
                "time_limit_minutes": test.time_limit_minutes,
                "attempts_count": a["attempts_count"] if a else 0,
                "passed": bool(a["passed_count"]) if a else None,
                "best_score": float(a["best_score"]) if a and a["best_score"] is not None else None,
            })

        return Response({"tests": results})

# ─── Admin exercise preview instance ─────────────────────────────────────────

class ExercisePreviewInstanceView(APIView):
    """
    GET /api/v1/progress/exercises/<exercise_id>/preview-instance/

    Admin-only. Generates and returns one random instance from the
    exercise template — same format as the practice endpoint, so the
    frontend can render it with the exact same ExerciseCard component.

    Does NOT record any attempt or session data.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, exercise_id):
        try:
            exercise = Exercise.objects.select_related("lesson").get(id=exercise_id)
        except Exercise.DoesNotExist:
            return Response({"error": "Exercițiul nu există."}, status=status.HTTP_404_NOT_FOUND)

        try:
            instance = generate_instance(exercise)
        except Exception as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            "instance": instance,
            "exercise_id": exercise.id,
            "lesson_title": exercise.lesson.title,
            "exercise_type": exercise.exercise_type,
            "difficulty": exercise.difficulty,
            "category": exercise.category or "",
        })
