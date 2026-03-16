"""
Progress API views for MathEd Romania.

Endpoints:
  POST /api/v1/progress/lessons/<id>/open/       — mark lesson in_progress
  POST /api/v1/progress/lessons/<id>/complete/   — mark lesson completed
  GET  /api/v1/progress/lessons/<id>/practice/   — get randomized exercise set
  POST /api/v1/progress/exercises/attempt/       — submit & grade an attempt
  GET  /api/v1/progress/dashboard/               — student dashboard stats
"""
from django.core import signing
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Exercise, Lesson
from apps.progress.models import ExerciseAttempt, LessonProgress, TestAttempt
from apps.progress.exercise_engine import decode_instance_token, generate_instance
from apps.progress.grading import grade_attempt
from apps.progress.serializers import AttemptSubmitSerializer, DashboardSerializer



# ─── Lesson open / complete ───────────────────────────────────────────────────

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


class LessonCompleteView(APIView):
    """
    POST /api/v1/progress/lessons/<lesson_id>/complete/

    Body (optional):
      { "time_spent_seconds": 240 }

    Marks the lesson as completed and records time spent.
    Only marks complete if the student has met the practice minimum
    for this lesson.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id, is_published=True)
        except Lesson.DoesNotExist:
            return Response({"error": "Lecția nu există."}, status=status.HTTP_404_NOT_FOUND)

        # Count correct attempts for this lesson's exercises
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

class LessonCategoriesView(APIView):
    """
    GET /api/v1/progress/lessons/<lesson_id>/categories/

    Returns all exercise categories for a lesson, with the student's
    attempt history and best session score (best X out of 5) per category.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lesson_id):
        from apps.content.models import Exercise, Lesson
        from django.db.models import Count, Q

        try:
            lesson = Lesson.objects.get(id=lesson_id, is_published=True)
        except Lesson.DoesNotExist:
            return Response({"error": "Lecția nu există."}, status=status.HTTP_404_NOT_FOUND)

        exercises = Exercise.objects.filter(lesson=lesson, is_active=True)

        # Group exercises by category
        category_map: dict[str, list] = {}
        for ex in exercises:
            cat = ex.category or ""
            if cat not in category_map:
                category_map[cat] = []
            category_map[cat].append(ex.id)

        if not category_map:
            return Response({
                "lesson_id": lesson_id,
                "lesson_title": lesson.title,
                "categories": [],
            })

        # Get all attempts for this lesson's exercises by this student
        all_attempts = ExerciseAttempt.objects.filter(
            student=request.user,
            exercise__lesson=lesson,
        ).values("exercise__category", "is_correct", "attempted_at").order_by("attempted_at")

        # Build per-category stats
        from collections import defaultdict
        cat_correct: dict[str, int] = defaultdict(int)
        cat_total: dict[str, int] = defaultdict(int)
        # Track chronological correct/incorrect per category for best session
        cat_attempts_timeline: dict[str, list] = defaultdict(list)

        for attempt in all_attempts:
            cat = attempt["exercise__category"] or ""
            cat_total[cat] += 1
            if attempt["is_correct"]:
                cat_correct[cat] += 1
            cat_attempts_timeline[cat].append(attempt["is_correct"])

        # Best session score: sliding window of 5, best consecutive 5
        def best_session_of_5(timeline: list) -> int | None:
            if not timeline:
                return None
            if len(timeline) < 5:
                return sum(timeline)
            best = 0
            for i in range(len(timeline) - 4):
                window = sum(timeline[i:i+5])
                if window > best:
                    best = window
            return best

        # Build response
        categories = []
        for cat, ex_ids in category_map.items():
            label = cat if cat else "Toate exercițiile"
            categories.append({
                "category": cat,
                "label": label,
                "exercise_count": len(ex_ids),
                "correct_attempts": cat_correct[cat],
                "total_attempts": cat_total[cat],
                "best_session_score": best_session_of_5(cat_attempts_timeline[cat]),
            })

        # Sort: uncategorized last, then alphabetical
        categories.sort(key=lambda c: ("" if c["category"] else "zzz", c["label"]))

        return Response({
            "lesson_id": lesson_id,
            "lesson_title": lesson.title,
            "categories": categories,
        })


# ─── Exercise serving ─────────────────────────────────────────────────────────

class LessonCategoriesView(APIView):
    """
    GET /api/v1/progress/lessons/<lesson_id>/categories/

    Returns all exercise categories for a lesson, with the student's
    attempt history and best session score (best X out of 5) per category.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lesson_id):
        from apps.content.models import Exercise, Lesson
        from django.db.models import Count, Q

        try:
            lesson = Lesson.objects.get(id=lesson_id, is_published=True)
        except Lesson.DoesNotExist:
            return Response({"error": "Lecția nu există."}, status=status.HTTP_404_NOT_FOUND)

        exercises = Exercise.objects.filter(lesson=lesson, is_active=True)

        # Group exercises by category
        category_map: dict[str, list] = {}
        for ex in exercises:
            cat = ex.category or ""
            if cat not in category_map:
                category_map[cat] = []
            category_map[cat].append(ex.id)

        if not category_map:
            return Response({
                "lesson_id": lesson_id,
                "lesson_title": lesson.title,
                "categories": [],
            })

        # Get all attempts for this lesson's exercises by this student
        all_attempts = ExerciseAttempt.objects.filter(
            student=request.user,
            exercise__lesson=lesson,
        ).values("exercise__category", "is_correct", "attempted_at").order_by("attempted_at")

        # Build per-category stats
        from collections import defaultdict
        cat_correct: dict[str, int] = defaultdict(int)
        cat_total: dict[str, int] = defaultdict(int)
        # Track chronological correct/incorrect per category for best session
        cat_attempts_timeline: dict[str, list] = defaultdict(list)

        for attempt in all_attempts:
            cat = attempt["exercise__category"] or ""
            cat_total[cat] += 1
            if attempt["is_correct"]:
                cat_correct[cat] += 1
            cat_attempts_timeline[cat].append(attempt["is_correct"])

        # Best session score: sliding window of 5, best consecutive 5
        def best_session_of_5(timeline: list) -> int | None:
            if not timeline:
                return None
            if len(timeline) < 5:
                return sum(timeline)
            best = 0
            for i in range(len(timeline) - 4):
                window = sum(timeline[i:i + 5])
                if window > best:
                    best = window
            return best

        # Build response
        categories = []
        for cat, ex_ids in category_map.items():
            label = cat if cat else "Toate exercițiile"
            categories.append({
                "category": cat,
                "label": label,
                "exercise_count": len(ex_ids),
                "correct_attempts": cat_correct[cat],
                "total_attempts": cat_total[cat],
                "best_session_score": best_session_of_5(cat_attempts_timeline[cat]),
            })

        # Sort: uncategorized last, then alphabetical
        categories.sort(key=lambda c: ("" if c["category"] else "zzz", c["label"]))

        return Response({
            "lesson_id": lesson_id,
            "lesson_title": lesson.title,
            "categories": categories,
        })


# ─── 2. Replace LessonPracticeView with this version ─────────────────────────
#       (adds ?category= filtering)

class LessonPracticeView(APIView):
    """
    GET /api/v1/progress/lessons/<lesson_id>/practice/?count=5&category=expanded_form

    Returns randomized exercise instances for the given lesson.
    Optional ?category= filters to a specific exercise category.
    Default count: 5. Max count: 20.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lesson_id):
        from apps.content.models import Lesson

        try:
            lesson = Lesson.objects.prefetch_related("exercises").get(
                id=lesson_id, is_published=True
            )
        except Lesson.DoesNotExist:
            return Response({"error": "Lecția nu există."}, status=status.HTTP_404_NOT_FOUND)

        category = request.query_params.get("category", None)

        qs = lesson.exercises.filter(is_active=True)
        if category is not None:
            # Empty string means "uncategorized"
            qs = qs.filter(category=category)

        exercises = list(qs)
        if not exercises:
            return Response(
                {"error": "Această lecție nu are exerciții active pentru categoria selectată."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            count = min(int(request.query_params.get("count", 5)), 20)
        except (ValueError, TypeError):
            count = 5

        import random
        if len(exercises) >= count:
            selected = random.sample(exercises, count)
        else:
            selected = random.choices(exercises, k=count)

        from apps.progress.exercise_engine import generate_instance
        instances = []
        for exercise in selected:
            try:
                instances.append(generate_instance(exercise))
            except Exception:
                continue

        return Response({
            "lesson_id": lesson_id,
            "exercises": instances,
            "practice_minimum": lesson.practice_minimum,
        })


# ─── Attempt submission ───────────────────────────────────────────────────────

class ExerciseAttemptView(APIView):
    """
    POST /api/v1/progress/exercises/attempt/

    Body:
      {
        "exercise_id": 42,
        "instance_token": "<signed token from practice endpoint>",
        "answer": "936"         // string, or list for drag_order
      }

    Response:
      {
        "is_correct": true,
        "correct_answer": "936",    // shown after wrong answers
        "error": null
      }
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

        # Verify the exercise exists
        try:
            exercise = Exercise.objects.get(id=exercise_id, is_active=True)
        except Exercise.DoesNotExist:
            return Response({"error": "Exercițiul nu există."}, status=status.HTTP_404_NOT_FOUND)

        # Decode the signed token
        try:
            token_data = decode_instance_token(instance_token)
        except signing.BadSignature:
            return Response(
                {"error": "Token invalid sau expirat. Reîncarcă exercițiul."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Sanity check: token must match the submitted exercise
        if token_data["exercise_id"] != exercise_id:
            return Response(
                {"error": "Token nepotrivit cu exercițiul."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        exercise_type = token_data["exercise_type"]
        grading_data = token_data["grading_data"]

        # Grade the attempt
        is_correct, error_msg = grade_attempt(exercise_type, student_answer, grading_data)

        # Persist the attempt
        ExerciseAttempt.objects.create(
            student=request.user,
            exercise=exercise,
            answer={"raw": student_answer},
            is_correct=is_correct,
        )

        # Build the correct answer display string
        correct_answer_display = _build_correct_display(exercise_type, grading_data)

        return Response({
            "is_correct": is_correct,
            "correct_answer": correct_answer_display if not is_correct else None,
            "error": error_msg,
        })


def _build_correct_display(exercise_type: str, grading_data: dict) -> str:
    """Build a human-readable correct answer string to show after a wrong attempt."""
    if exercise_type == "fill_blank":
        return grading_data.get("correct_expr", "")
    elif exercise_type == "comparison":
        left = grading_data.get("left_expr", "")
        right = grading_data.get("right_expr", "")
        # Re-evaluate to get the correct symbol
        from apps.progress.grading import grade_comparison
        _, _ = grade_comparison("?", left, right)
        # Actually, recompute the relation properly
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
            l = parse_expr(left.replace(":", "/"), transformations=transforms)
            r = parse_expr(right.replace(":", "/"), transformations=transforms)
            diff = sympy.simplify(l - r)
            if diff == sympy.Integer(0):
                return "="
            elif diff > 0:
                return ">"
            else:
                return "<"
        except Exception:  # noqa: BLE001
            return "?"
    elif exercise_type == "multiple_choice":
        return grading_data.get("correct_option_id", "")
    elif exercise_type == "drag_order":
        return ", ".join(str(x) for x in grading_data.get("correct_order", []))
    return ""


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardView(APIView):
    """
    GET /api/v1/progress/dashboard/

    Returns aggregated stats for the authenticated student's dashboard:
      - Overall lesson completion counts
      - Per-unit breakdown
      - Exercise attempt accuracy
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.content.models import Grade, Unit

        user = request.user

        # All lessons in the platform (published)
        from apps.content.models import Lesson
        all_lessons = Lesson.objects.filter(is_published=True).select_related("unit__grade")

        # Student's progress rows
        progress_map = {
            p.lesson_id: p.status
            for p in LessonProgress.objects.filter(student=user)
        }

        total_lessons = all_lessons.count()
        completed = sum(
            1 for l in all_lessons
            if progress_map.get(l.id) == LessonProgress.Status.COMPLETED
        )
        in_progress = sum(
            1 for l in all_lessons
            if progress_map.get(l.id) == LessonProgress.Status.IN_PROGRESS
        )

        # Attempt stats
        attempts = ExerciseAttempt.objects.filter(student=user)
        total_attempts = attempts.count()
        correct_attempts = attempts.filter(is_correct=True).count()
        accuracy = (
            round((correct_attempts / total_attempts) * 100, 1)
            if total_attempts > 0 else 0.0
        )

        # Per-unit breakdown
        units_data = []
        for unit in Unit.objects.filter(is_published=True).prefetch_related(
            "lessons", "grade"
        ).order_by("grade__number", "order"):
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
            "total_attempts": total_attempts,
            "correct_attempts": correct_attempts,
            "accuracy_percent": accuracy,
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

        # Resume existing in-progress attempt if any
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

        # Build fresh session
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
        "attempt_id": 1,
        "index": 0,
        "instance_token": "...",
        "answer": "936"
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

        # Decode token and grade
        try:
            token_data = decode_instance_token(instance_token)
        except signing.BadSignature:
            return Response({"error": "Token invalid."}, status=status.HTTP_400_BAD_REQUEST)

        exercise_type = token_data["exercise_type"]
        grading_data = token_data["grading_data"]
        is_correct, error_msg = grade_attempt(exercise_type, student_answer, grading_data)

        # Get weight from stored instance
        instances = attempt.exercise_instances
        weight = instances[int(index)].get("weight", 10) if int(index) < len(instances) else 10

        # Store answer
        answers = attempt.answers
        answers[str(index)] = {
            "answer": student_answer,
            "is_correct": is_correct,
            "exercise_id": token_data.get("exercise_id"),
            "weight": weight,
        }
        attempt.answers = answers
        attempt.save(update_fields=["answers"])

        # During a test we don't reveal correctness — just acknowledge receipt
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
