"""
Progress API views for MathEd Romania.

Endpoints:
  POST /api/v1/progress/lessons/<id>/open/          — mark lesson in_progress
  POST /api/v1/progress/lessons/<id>/complete/      — mark lesson completed
  GET  /api/v1/progress/topics/<id>/practice/       — get randomized exercise set
  GET  /api/v1/progress/topics/<id>/categories/     — category list with tier states
  POST /api/v1/progress/exercises/attempt/          — submit & grade an attempt
  GET  /api/v1/progress/exercises-overview/         — all topics with exercises
  GET  /api/v1/progress/tests-overview/             — all topic tests
  GET  /api/v1/progress/dashboard/                  — student dashboard stats
"""
import logging
import uuid
from collections import defaultdict
from datetime import timedelta

from django.core.signing import SignatureExpired
from django.db.models import Case, Count, IntegerField, When
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Exercise, Lesson, Topic, Test
from apps.progress.exercise_engine import decode_instance_token, generate_instance
from apps.progress.grading import grade_attempt
from apps.progress.models import (
    CategoryProgress,
    ExerciseAttempt,
    LessonProgress,
    Streak,
    StreakActivity,
    TestAttempt,
)
from apps.progress.serializers import (
    AttemptSubmitSerializer,
    DashboardSerializer,
    StreakSerializer,
)
from apps.progress.streak_service import _today_local, record_activity

logger = logging.getLogger(__name__)


# ─── Lesson open ──────────────────────────────────────────────────────────────

class LessonOpenView(APIView):
    """
    POST /api/v1/progress/lessons/<lesson_id>/open/

    Called when a student opens a lesson. Creates or updates a
    LessonProgress row with status=in_progress. Idempotent.
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

        if created:
            try:
                record_activity(request.user, "lesson")
            except Exception:
                logger.warning("Streak update failed", exc_info=True)

        if not created and progress.status == LessonProgress.Status.NOT_STARTED:
            progress.status = LessonProgress.Status.IN_PROGRESS
            progress.save(update_fields=["status"])

        return Response({"lesson_id": lesson_id, "status": progress.status})


# ─── Lesson complete ──────────────────────────────────────────────────────────

class LessonCompleteView(APIView):
    """
    POST /api/v1/progress/lessons/<lesson_id>/complete/

    Marks a lesson as completed. No practice minimum check here —
    that gate is at the topic level (test unlock).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id, is_published=True)
        except Lesson.DoesNotExist:
            return Response({"error": "Lecția nu există."}, status=status.HTTP_404_NOT_FOUND)

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


# ─── Topic practice session ───────────────────────────────────────────────────

class TopicPracticeView(APIView):
    """
    GET /api/v1/progress/topics/<topic_id>/practice/
        ?count=5
        &category=expanded_form   (optional)
        &difficulty=easy          (optional)

    Returns a randomized batch of exercise instances for practice.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, topic_id):
        try:
            topic = Topic.objects.prefetch_related("exercises").get(
                id=topic_id, is_published=True
            )
        except Topic.DoesNotExist:
            return Response({"error": "Tema nu există."}, status=status.HTTP_404_NOT_FOUND)

        count = int(request.query_params.get("count", 5))
        category = request.query_params.get("category", None)
        difficulty = request.query_params.get("difficulty", None)

        exercises = topic.exercises.filter(is_active=True)
        if category is not None:
            exercises = exercises.filter(category=category)
        if difficulty:
            exercises = exercises.filter(difficulty=difficulty)

        exercises = list(exercises)

        if not exercises:
            return Response(
                {"error": "Nu există exerciții disponibile pentru acest filtru."},
                status=status.HTTP_404_NOT_FOUND,
            )

        import random
        if len(exercises) <= count:
            selected = exercises * (count // len(exercises) + 1)
            selected = selected[:count]
        else:
            selected = random.sample(exercises, count)

        session_id = str(uuid.uuid4())

        instances = []
        for ex in selected:
            try:
                instance = generate_instance(ex)
                instance["exercise_id"] = ex.id
                instances.append(instance)
            except Exception as e:
                continue

        hint_active_categories = list(
            CategoryProgress.objects.filter(
                student=request.user,
                topic=topic,
                category_failure_count__gte=2,
            ).values_list("category", flat=True)
        )

        return Response({
            "topic_id": topic_id,
            "session_id": session_id,
            "exercises": instances,
            "practice_minimum": topic.practice_minimum,
            "hint_active_categories": hint_active_categories,
        })


# ─── Topic categories ─────────────────────────────────────────────────────────

class TopicCategoriesView(APIView):
    """
    GET /api/v1/progress/topics/<topic_id>/categories/

    Returns all exercise categories for a topic with tier states.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, topic_id):
        try:
            topic = Topic.objects.get(id=topic_id, is_published=True)
        except Topic.DoesNotExist:
            return Response({"error": "Tema nu există."}, status=status.HTTP_404_NOT_FOUND)

        exercises = Exercise.objects.filter(topic=topic, is_active=True)

        # Group exercise IDs by category
        category_map: dict[str, list[int]] = {}
        for ex in exercises:
            cat = ex.category or ""
            category_map.setdefault(cat, []).append(ex.id)

        if not category_map:
            return Response({
                "topic_id": topic_id,
                "topic_title": topic.title,
                "categories": [],
            })

        # Attempt counts per category
        cat_total: dict[str, int] = defaultdict(int)
        for attempt in ExerciseAttempt.objects.filter(
            student=request.user,
            exercise__topic=topic,
        ).values("exercise__category"):
            cat_total[attempt["exercise__category"] or ""] += 1

        # Perfect batch counts per category
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

        # CategoryProgress tier states
        cp_map: dict[str, CategoryProgress] = {
            cp.category: cp
            for cp in CategoryProgress.objects.filter(student=request.user, topic=topic)
        }

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
                    "easy":   {"available": True,          "cleared": easy_cleared},
                    "medium": {"available": easy_cleared,  "cleared": medium_cleared},
                    "hard":   {"available": easy_cleared,  "cleared": hard_cleared},
                },
            })

        categories.sort(key=lambda c: ("zzz" if not c["category"] else "", c["label"]))

        return Response({
            "topic_id": topic_id,
            "topic_title": topic.title,
            "categories": categories,
        })


# ─── Exercise attempt ─────────────────────────────────────────────────────────

class ExerciseAttemptView(APIView):
    """
    POST /api/v1/progress/exercises/attempt/

    Grades a single exercise attempt and records it.
    Checks for perfect batch tier unlocks.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AttemptSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        exercise_id = data["exercise_id"]
        instance_token = data["instance_token"]
        answer = data["answer"]
        session_id = data.get("session_id")
        is_preview = request.query_params.get("preview") == "true"

        try:
            exercise = Exercise.objects.select_related("topic").get(id=exercise_id)
        except Exercise.DoesNotExist:
            return Response({"error": "Exercițiul nu există."}, status=status.HTTP_404_NOT_FOUND)

        try:
            payload = decode_instance_token(instance_token)
            grading_data = payload.get("grading_data", payload)
        except SignatureExpired:
            return Response(
                {"error": "Exercițiul a expirat. Te rugăm să generezi unul nou.", "expired": True},
                status=status.HTTP_410_GONE,
            )
        except Exception:
            return Response({"error": "Token invalid."}, status=status.HTTP_400_BAD_REQUEST)

        is_correct, error = grade_attempt(
            exercise.exercise_type,
            answer,
            grading_data,
        )

        correct_display = _correct_answer_display(exercise.exercise_type, grading_data) if not is_correct else None

        # Build follow-up data if this is a multi-answer exercise and student got it right
        follow_up = None
        if is_correct and "correct_exprs" in grading_data and error is not None:
            try:
                matched_idx = int(error)
                other_idx = 1 - matched_idx
                other_expr = grading_data["correct_exprs"][other_idx]
                try:
                    from apps.progress.grading import TRANSFORMATIONS, normalize
                    from sympy.parsing.sympy_parser import parse_expr
                    other_value = str(parse_expr(normalize(other_expr), transformations=TRANSFORMATIONS))
                except Exception:
                    other_value = other_expr
                follow_up = {
                    "question": grading_data.get("follow_up_question", ""),
                    "expected": other_value,
                }
            except (ValueError, IndexError):
                pass

        if is_preview:
            return Response({
                "is_correct": is_correct,
                "correct_answer": correct_display,
                "follow_up": follow_up,
                "tier_cleared": None,
                "hint_active_for_category": None,
                "error": error if not is_correct else None,
            })

        ExerciseAttempt.objects.create(
            student=request.user,
            exercise=exercise,
            answer=answer,
            is_correct=is_correct,
            session_id=session_id,
        )

        try:
            record_activity(request.user, "exercise")
        except Exception:
            logger.warning("Streak update failed", exc_info=True)

        # ── Hint counter update ──────────────────────────────────────
        if not is_correct and session_id and exercise.category:
            prior_wrong = ExerciseAttempt.objects.filter(
                student=request.user,
                session_id=session_id,
                exercise__category=exercise.category,
                is_correct=False,
            ).count()
            # prior_wrong includes the attempt we just created; "first wrong"
            # means exactly 1 wrong attempt exists for this batch+category.
            if prior_wrong == 1:
                now = timezone.now()
                cp, _ = CategoryProgress.objects.get_or_create(
                    student=request.user,
                    topic=exercise.topic,
                    category=exercise.category,
                )
                if cp.last_failure_at is None or now - cp.last_failure_at > timedelta(days=7):
                    cp.category_failure_count = 1
                else:
                    cp.category_failure_count += 1
                cp.last_failure_at = now
                cp.save(update_fields=["category_failure_count", "last_failure_at"])

        # ── Determine hint_active_for_category ───────────────────────
        hint_active_for_category = None
        if exercise.category:
            cp = CategoryProgress.objects.filter(
                student=request.user,
                topic=exercise.topic,
                category=exercise.category,
            ).first()
            if cp and cp.category_failure_count >= 2:
                hint_active_for_category = exercise.category

        tier_cleared = None
        if session_id:
            tier_cleared = self._check_tier_cleared(request.user, session_id, exercise)

        correct_display = _correct_answer_display(exercise.exercise_type, grading_data) if not is_correct else None

        return Response({
            "is_correct": is_correct,
            "correct_answer": correct_display,
            "follow_up": follow_up,
            "tier_cleared": tier_cleared,
            "hint_active_for_category": hint_active_for_category,
            "error": error if not is_correct else None,
        })

    def _check_tier_cleared(self, user, session_id, exercise):
        batch = ExerciseAttempt.objects.filter(student=user, session_id=session_id)
        if batch.count() != 5:
            return None
        if batch.filter(is_correct=False).exists():
            return None

        difficulty = exercise.difficulty
        category = exercise.category
        topic = exercise.topic

        cp, _ = CategoryProgress.objects.get_or_create(
            student=user,
            topic=topic,
            category=category,
        )

        if difficulty == "easy" and not cp.easy_cleared:
            cp.easy_cleared = True
            cp.save(update_fields=["easy_cleared"])
            return {"tier": "easy", "also_cleared": []}
        elif difficulty == "medium" and not cp.medium_cleared:
            cp.medium_cleared = True
            cp.save(update_fields=["medium_cleared"])
            return {"tier": "medium", "also_cleared": []}
        elif difficulty == "hard" and not cp.hard_cleared:
            cp.hard_cleared = True
            also_cleared = []
            if not cp.medium_cleared:
                cp.medium_cleared = True
                also_cleared.append("medium")
                cp.save(update_fields=["hard_cleared", "medium_cleared"])
            else:
                cp.save(update_fields=["hard_cleared"])
            return {"tier": "hard", "also_cleared": also_cleared}

        return None


# ─── Hint used ───────────────────────────────────────────────────────────────

class HintUsedView(APIView):
    """
    POST /api/v1/progress/categories/hint-used/

    Called when a student uses a hint. Resets the failure counter
    for the given (student, topic, category).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        topic_id = request.data.get("topic_id")
        category = request.data.get("category")

        if (
            not isinstance(topic_id, int)
            or topic_id <= 0
            or not isinstance(category, str)
            or not category
        ):
            return Response(
                {"error": "topic_id și category sunt obligatorii."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated = CategoryProgress.objects.filter(
            student=request.user,
            topic_id=topic_id,
            category=category,
        ).update(category_failure_count=0)

        return Response({"reset": updated > 0})


# ─── Exercises overview ───────────────────────────────────────────────────────

class ExercisesOverviewView(APIView):
    """
    GET /api/v1/progress/exercises-overview/

    Returns all published topics that have at least one active exercise,
    ordered by unit then topic, with per-topic aggregate progress.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        topics = (
            Topic.objects
            .filter(is_published=True, exercises__is_active=True)
            .distinct()
            .select_related("unit__grade")
            .order_by("unit__order", "order")
        )
        topic_ids = [t.id for t in topics]

        # Total distinct exercise categories per topic
        cat_counts = (
            Exercise.objects
            .filter(topic_id__in=topic_ids, is_active=True)
            .values("topic_id")
            .annotate(total=Count("category", distinct=True))
        )
        cat_count_map = {row["topic_id"]: row["total"] for row in cat_counts}

        # Completed categories (medium or hard cleared)
        completed_by_topic: dict[int, int] = defaultdict(int)
        for cp in CategoryProgress.objects.filter(student=user, topic_id__in=topic_ids):
            if cp.medium_cleared or cp.hard_cleared:
                completed_by_topic[cp.topic_id] += 1

        # Exercises attempted per topic
        attempt_count_map: dict[int, int] = {}
        for row in (
            ExerciseAttempt.objects
            .filter(student=user, exercise__topic_id__in=topic_ids)
            .values("exercise__topic_id")
            .annotate(count=Count("id"))
        ):
            attempt_count_map[row["exercise__topic_id"]] = row["count"]

        results = [
            {
                "topic_id": topic.id,
                "topic_title": topic.title,
                "unit_id": topic.unit_id,
                "unit_title": topic.unit.title,
                "unit_order": topic.unit.order,
                "topic_order": topic.order,
                "total_categories": cat_count_map.get(topic.id, 0),
                "completed_categories": completed_by_topic.get(topic.id, 0),
                "exercises_attempted": attempt_count_map.get(topic.id, 0),
            }
            for topic in topics
        ]

        return Response({"topics": results})


# ─── Tests overview ───────────────────────────────────────────────────────────

class TestsOverviewView(APIView):
    """
    GET /api/v1/progress/tests-overview/

    Returns all published topic tests ordered by topic sequence,
    with the authenticated student's best attempt status.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.db import models as django_models

        user = request.user

        tests = (
            Test.objects
            .filter(scope=Test.Scope.TOPIC, is_published=True, topic__is_published=True)
            .select_related("topic__unit__grade")
            .order_by("topic__unit__order", "topic__order")
        )
        test_ids = [t.id for t in tests]

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
                passed_count=Count("id", filter=django_models.Q(passed=True)),
                best_score=django_models.Max("score"),
            )
        )
        attempt_map = {row["test_id"]: row for row in attempt_stats}

        results = []
        for test in tests:
            a = attempt_map.get(test.id)
            results.append({
                "test_id": test.id,
                "topic_id": test.topic_id,
                "topic_title": test.topic.title,
                "unit_id": test.topic.unit_id,
                "unit_title": test.topic.unit.title,
                "unit_order": test.topic.unit.order,
                "topic_order": test.topic.order,
                "pass_threshold": test.pass_threshold,
                "time_limit_minutes": test.time_limit_minutes,
                "attempts_count": a["attempts_count"] if a else 0,
                "passed": bool(a["passed_count"]) if a else None,
                "best_score": float(a["best_score"]) if a and a["best_score"] is not None else None,
            })

        return Response({"tests": results})


# ─── Exercise preview (admin) ─────────────────────────────────────────────────

class ExercisePreviewInstanceView(APIView):
    """
    GET /api/v1/progress/exercises/<exercise_id>/preview-instance/

    Generates and returns one random instance without recording any attempt.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, exercise_id):
        try:
            exercise = Exercise.objects.select_related("topic").get(id=exercise_id)
        except Exercise.DoesNotExist:
            return Response({"error": "Exercițiul nu există."}, status=status.HTTP_404_NOT_FOUND)

        try:
            instance = generate_instance(exercise)
            instance["exercise_id"] = exercise.id
        except Exception as e:
            return Response(
                {"error": f"Template invalid: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            "instance": instance,
            "exercise_id": exercise.id,
            "topic_title": exercise.topic.title,
            "exercise_type": exercise.exercise_type,
            "difficulty": exercise.difficulty,
            "category": exercise.category,
        })


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardView(APIView):
    """
    GET /api/v1/progress/dashboard/

    Aggregated stats for the authenticated student.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.content.models import Unit
        from django.db import models as django_models

        user = request.user

        all_lessons = Lesson.objects.filter(is_published=True).select_related("topic__unit__grade")
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

        units = Unit.objects.filter(is_published=True).prefetch_related(
            "topics__lessons"
        ).select_related("grade").order_by("grade", "order")

        unit_data = []
        for unit in units:
            unit_lessons = [
                l for topic in unit.topics.filter(is_published=True)
                for l in topic.lessons.filter(is_published=True)
            ]
            unit_completed = sum(
                1 for l in unit_lessons
                if progress_map.get(l.id) == LessonProgress.Status.COMPLETED
            )
            unit_data.append({
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
            "units": unit_data,
        })


# ─── Streak ───────────────────────────────────────────────────────────────────

class StreakView(APIView):
    """
    GET /api/v1/progress/streak/

    Returns the authenticated student's streak stats and activity
    history for the calendar heatmap.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        streak, _ = Streak.objects.get_or_create(student=request.user)

        cutoff = _today_local() - timedelta(days=365)
        active_dates = list(
            StreakActivity.objects
            .filter(student=request.user, date__gte=cutoff)
            .order_by("date")
            .values_list("date", flat=True)
        )

        data = {
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "freeze_count": streak.freeze_count,
            "active_dates": active_dates,
        }

        serializer = StreakSerializer(data)
        return Response(serializer.data)


# ─── Test session views ───────────────────────────────────────────────────────

class TestStartView(APIView):
    """POST /api/v1/progress/tests/<test_id>/start/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, test_id):
        try:
            test = Test.objects.get(id=test_id, is_published=True)
        except Test.DoesNotExist:
            return Response({"error": "Testul nu există."}, status=status.HTTP_404_NOT_FOUND)

        # Reuse existing in-progress attempt if any
        attempt = TestAttempt.objects.filter(
            student=request.user,
            test=test,
            status=TestAttempt.Status.IN_PROGRESS,
        ).first()

        if not attempt:
            # Generate exercises from composition
            exercises_pool = Exercise.objects.filter(
                topic=test.topic, is_active=True
            ) if test.topic else Exercise.objects.filter(
                topic__unit=test.unit, is_active=True
            )

            instances = _build_test_instances(test.composition, exercises_pool)
            attempt = TestAttempt.objects.create(
                student=request.user,
                test=test,
                exercise_instances=instances,
                status=TestAttempt.Status.IN_PROGRESS,
            )

        return Response({
            "attempt_id": attempt.id,
            "exercises": attempt.exercise_instances,
            "answers": attempt.answers,
        })


class TestAnswerView(APIView):
    """POST /api/v1/progress/tests/<test_id>/answer/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, test_id):
        attempt = TestAttempt.objects.filter(
            student=request.user,
            test_id=test_id,
            status=TestAttempt.Status.IN_PROGRESS,
        ).first()

        if not attempt:
            return Response({"error": "Nu există un test activ."}, status=status.HTTP_404_NOT_FOUND)

        index = str(request.data.get("index"))
        answer = request.data.get("answer")

        answers = dict(attempt.answers)
        answers[index] = {"answer": answer, "is_correct": None, "exercise_id": None}
        attempt.answers = answers
        attempt.save(update_fields=["answers"])

        return Response({"saved": True})


class TestFinishView(APIView):
    """POST /api/v1/progress/tests/<test_id>/finish/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, test_id):
        attempt = TestAttempt.objects.filter(
            student=request.user,
            test_id=test_id,
            status=TestAttempt.Status.IN_PROGRESS,
        ).first()

        if not attempt:
            return Response({"error": "Nu există un test activ."}, status=status.HTTP_404_NOT_FOUND)

        test = attempt.test
        instances = attempt.exercise_instances
        answers = dict(attempt.answers)

        total_weight = 0
        earned_weight = 0
        graded_answers = {}

        for idx, instance in enumerate(instances):
            str_idx = str(idx)
            exercise_id = instance.get("exercise_id")
            instance_token = instance.get("instance_token")
            weight = instance.get("weight", 1)
            student_answer = answers.get(str_idx, {}).get("answer")

            total_weight += weight

            if student_answer is None or instance_token is None:
                graded_answers[str_idx] = {
                    "answer": None,
                    "is_correct": False,
                    "exercise_id": exercise_id,
                }
                continue

            try:
                exercise = Exercise.objects.get(id=exercise_id)
                payload = decode_instance_token(instance_token)
                grading_data = payload.get("grading_data", payload)
                is_correct, correct_answer = grade_attempt(
                    exercise.exercise_type, student_answer, grading_data
                )
            except SignatureExpired:
                return Response(
                    {"error": "Testul a expirat. Te rugăm să începi unul nou.", "expired": True},
                    status=status.HTTP_410_GONE,
                )
            except Exception:
                is_correct = False
                correct_answer = None

            if is_correct:
                earned_weight += weight

            graded_answers[str_idx] = {
                "answer": student_answer,
                "is_correct": is_correct,
                "correct_answer": correct_answer,
                "exercise_id": exercise_id,
            }

        score = (earned_weight / total_weight * 100) if total_weight > 0 else 0
        passed = score >= test.pass_threshold

        attempt.answers = graded_answers
        attempt.score = score
        attempt.passed = passed
        attempt.status = TestAttempt.Status.COMPLETED
        attempt.finished_at = timezone.now()
        attempt.save()

        try:
            act_type = "topic_test" if test.scope == "topic" else "unit_test"
            record_activity(request.user, act_type)
        except Exception:
            logger.warning("Streak update failed", exc_info=True)

        return Response({
            "attempt_id": attempt.id,
            "score": round(score, 2),
            "passed": passed,
            "pass_threshold": test.pass_threshold,
            "answers": graded_answers,
        })


class TestResultView(APIView):
    """GET /api/v1/progress/tests/<test_id>/result/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, test_id):
        attempt = TestAttempt.objects.filter(
            student=request.user,
            test_id=test_id,
            status=TestAttempt.Status.COMPLETED,
        ).order_by("-finished_at").first()

        if not attempt:
            return Response({"error": "Nu există rezultate."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "attempt_id": attempt.id,
            "score": float(attempt.score),
            "passed": attempt.passed,
            "pass_threshold": attempt.test.pass_threshold,
            "answers": attempt.answers,
            "finished_at": attempt.finished_at,
        })


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _build_test_instances(composition: list, exercises_pool) -> list:
    """Build a list of exercise instances from a test composition spec."""
    import random
    instances = []

    for slot in composition:
        category = slot.get("category")
        count = slot.get("count", 1)
        difficulty = slot.get("difficulty")
        weight = slot.get("weight", 1)

        pool = exercises_pool.filter(category=category, is_active=True)
        if difficulty:
            pool = pool.filter(difficulty=difficulty)
        pool = list(pool)

        if not pool:
            continue

        selected = random.choices(pool, k=count)
        for ex in selected:
            try:
                instance = generate_instance(ex)
                instance["exercise_id"] = ex.id
                instance["weight"] = weight
                instances.append(instance)
            except Exception:
                continue

    return instances


def _correct_answer_display(exercise_type: str, grading_data: dict) -> str:
    """Return a human-readable correct answer string."""
    if exercise_type == "multi_fill_blank":
        parts = [f"{k} = {v}" for k, v in grading_data.get("correct_map", {}).items()]
        return ", ".join(parts)
    elif exercise_type == "fill_blank":
        if "correct_exprs" in grading_data:
            displays = []
            for expr in grading_data["correct_exprs"]:
                try:
                    from apps.progress.grading import TRANSFORMATIONS, normalize
                    from sympy.parsing.sympy_parser import parse_expr
                    displays.append(str(parse_expr(normalize(expr), transformations=TRANSFORMATIONS)))
                except Exception:
                    displays.append(expr)
            return " sau ".join(displays)
        if "valid_set" in grading_data:
            if grading_data.get("answer_display"):
                return grading_data["answer_display"]
            valid = grading_data["valid_set"]
            return f"orice număr din intervalul [{min(valid)}, {max(valid)}]"
        expr = grading_data.get("correct_expr", "")
        try:
            from apps.progress.grading import TRANSFORMATIONS, normalize
            from sympy.parsing.sympy_parser import parse_expr
            return str(parse_expr(normalize(expr), transformations=TRANSFORMATIONS))
        except Exception:
            return expr
    elif exercise_type == "comparison":
        left = grading_data.get("left_expr", "")
        right = grading_data.get("right_expr", "")
        try:
            import sympy
            from sympy.parsing.sympy_parser import (
                convert_xor, implicit_multiplication_application,
                parse_expr, standard_transformations,
            )
            transforms = standard_transformations + (
                implicit_multiplication_application, convert_xor,
            )
            l_val = parse_expr(left.replace(":", "/"), transformations=transforms)
            r_val = parse_expr(right.replace(":", "/"), transformations=transforms)
            diff = sympy.simplify(l_val - r_val)
            if diff == sympy.Integer(0):
                return "="
            return ">" if diff > 0 else "<"
        except Exception:
            return "?"
    elif exercise_type == "multiple_choice":
        return str(grading_data.get("correct_option_id", ""))
    elif exercise_type == "drag_order":
        return ", ".join(str(x) for x in grading_data.get("correct_order", []))
    return ""
