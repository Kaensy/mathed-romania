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
from django.db.models import Case, Count, F, IntegerField, When
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Exercise, Lesson, Topic, Test
from apps.progress.exercise_engine import decode_instance_token, generate_instance
from apps.progress.grading import grade_attempt
from apps.progress.unlock import get_passed_test_ids, get_test_unlock_map, is_test_unlocked
from apps.progress.models import (
    CategoryProgress,
    DailyTestSession,
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
from apps.progress.badges.service import evaluate_badges_for_event, serialize_badges
from apps.progress.categories.display_names import get_display_name
from apps.progress.cosmetics.service import (
    AvatarSourceError,
    CosmeticEquipError,
    InvalidAvatarUpload,
    build_catalog_state,
    equip_cosmetic,
    owned_slugs,
    serialize_cosmetics,
    set_avatar_source,
    upload_avatar,
)
from apps.progress.streak_service import (
    _today_local,
    evaluate_streak_badges_for,
    record_activity,
)
from apps.progress.xp import (
    award_xp,
    content_grade_for_topic,
    content_grade_for_unit,
)

logger = logging.getLogger(__name__)


def _topic_mastery_after_attempt(attempt) -> str | None:
    """Return current mastery tier for a passed topic-test attempt:
    one of "passed", "mastered", "perfect", or None when not topic-scoped
    or the attempt didn't pass.

    Mirrors the tier logic in `apps.content.views._build_topic_mastery_map`,
    narrowed to a single topic. Idempotency on each `topic_*` award means
    we can safely fire all qualifying tiers — earlier grants no-op.
    """
    test = attempt.test
    if test.scope != "topic" or test.topic_id is None or not attempt.passed:
        return None

    tier = "passed"
    categories = set(
        Exercise.objects
        .filter(topic_id=test.topic_id, is_active=True)
        .values_list("category", flat=True)
    )
    if not categories:
        return tier

    cleared = list(
        CategoryProgress.objects
        .filter(student=attempt.student_id, topic_id=test.topic_id)
        .values("category", "medium_cleared", "hard_cleared")
    )
    medium = {row["category"] for row in cleared if row["medium_cleared"]}
    if not categories.issubset(medium):
        return tier
    tier = "mastered"

    if attempt.score is not None and attempt.score >= 100:
        hard = {row["category"] for row in cleared if row["hard_cleared"]}
        if categories.issubset(hard):
            tier = "perfect"
    return tier


def _award_test_passed_xp(user, attempt) -> int:
    """Awards topic_passed/mastered/perfect (cumulatively, per current
    mastery state) for a topic test, or unit_passed for a unit test.

    Test progression is content-based, so XP routes to the *content's*
    grade (unit → grade for a unit test, topic → unit → grade for a
    topic test), not the student's current grade. Returns total XP
    granted by this call (0s from idempotency dedupe, or an
    unresolvable content grade)."""
    test = attempt.test
    if test.scope == "unit" and test.unit_id is not None:
        grade = content_grade_for_unit(test.unit_id)
        if grade is None:
            return 0
        return award_xp(
            user, "unit_passed", {"unit_id": test.unit_id}, grade,
        )

    tier = _topic_mastery_after_attempt(attempt)
    if tier is None:
        return 0

    grade = content_grade_for_topic(test.topic_id)
    if grade is None:
        return 0

    total = 0
    ctx = {"topic_id": test.topic_id}
    total += award_xp(user, "topic_passed", ctx, grade)
    if tier in ("mastered", "perfect"):
        total += award_xp(user, "topic_mastered", ctx, grade)
    if tier == "perfect":
        total += award_xp(user, "topic_perfect", ctx, grade)
    return total


def _safe_record_quest_progress(user, event: str, context: dict | None = None) -> None:
    """Fire a quest-progress event defensively.

    Lazy import + swallow, per the Block 10 cross-system-hook
    convention: a quest-counter bug must never roll back the view's
    primary mutation (graded attempt, finished test, …).
    """
    try:
        from apps.progress.quests.service import record_quest_progress
        record_quest_progress(user, event, context)
    except Exception:
        logger.warning(
            "Quest progress update failed for event=%s", event, exc_info=True,
        )


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

        # Snapshot owned cosmetics for the post-request diff. Any unlock
        # the XP grant or badge evaluator triggers below will show up in
        # `newly_unlocked_cosmetics`. One indexed query; non-students
        # get the empty set and a stable empty diff.
        cosmetics_before = owned_slugs(request.user)

        progress, created = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson,
            defaults={"status": LessonProgress.Status.IN_PROGRESS},
        )

        xp_gained = 0
        streak_badges: list[str] = []
        if created:
            try:
                xp_gained += record_activity(request.user, "lesson")
                streak_badges = evaluate_streak_badges_for(request.user)
            except Exception:
                logger.warning("Streak update failed", exc_info=True)

            grade = content_grade_for_topic(lesson.topic_id)
            if grade is not None:
                try:
                    xp_gained += award_xp(
                        request.user,
                        "lesson_first_open",
                        {"lesson_id": lesson.id},
                        grade,
                    )
                except Exception:
                    logger.warning("XP award failed", exc_info=True)

        if not created and progress.status == LessonProgress.Status.NOT_STARTED:
            progress.status = LessonProgress.Status.IN_PROGRESS
            progress.save(update_fields=["status"])

        own_badges: list[str] = []
        try:
            own_badges = evaluate_badges_for_event(
                request.user, "lesson_opened", {"lesson": lesson},
            )
        except Exception:
            logger.warning("Badge evaluation failed", exc_info=True)

        return Response({
            "lesson_id": lesson_id,
            "status": progress.status,
            "newly_earned_badges": serialize_badges(streak_badges + own_badges),
            "newly_unlocked_cosmetics": serialize_cosmetics(
                owned_slugs(request.user) - cosmetics_before
            ),
            "xp_gained": xp_gained,
        })


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
        easy_clear_count = 0
        medium_clear_count = 0
        hard_clear_count = 0
        # Empty-category buckets never get a CategoryProgress row, so they
        # can't be cleared and would block is_perfect — exclude them from
        # the denominator.
        total_real_categories = 0
        for cat, ex_ids in category_map.items():
            label = get_display_name(cat) if cat else "Toate exercițiile"
            cp = cp_map.get(cat)

            easy_cleared = cp.easy_cleared if cp else False
            medium_cleared = cp.medium_cleared if cp else False
            hard_cleared = cp.hard_cleared if cp else False
            all_tiers_cleared = easy_cleared and medium_cleared and hard_cleared

            if cat:
                total_real_categories += 1
                if easy_cleared:
                    easy_clear_count += 1
                if medium_cleared:
                    medium_clear_count += 1
                if hard_cleared:
                    hard_clear_count += 1

            categories.append({
                "category": cat,
                "label": label,
                "exercise_count": len(ex_ids),
                "exercises_attempted": cat_total[cat],
                "perfect_batches": cat_perfect[cat],
                "easy_cleared": easy_cleared,
                "medium_cleared": medium_cleared,
                "hard_cleared": hard_cleared,
                "all_tiers_cleared": all_tiers_cleared,
                "tiers": {
                    "easy":   {"available": True,          "cleared": easy_cleared},
                    "medium": {"available": easy_cleared,  "cleared": medium_cleared},
                    "hard":   {"available": easy_cleared,  "cleared": hard_cleared},
                },
            })

        categories.sort(key=lambda c: ("zzz" if not c["category"] else "", c["label"]))

        is_perfect = (
            total_real_categories > 0
            and easy_clear_count == total_real_categories
            and medium_clear_count == total_real_categories
            and hard_clear_count == total_real_categories
        )

        return Response({
            "topic_id": topic_id,
            "topic_title": topic.title,
            "categories": categories,
            "total_categories": total_real_categories,
            "easy_clear_count": easy_clear_count,
            "medium_clear_count": medium_clear_count,
            "hard_clear_count": hard_clear_count,
            "is_perfect": is_perfect,
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

        # Past the preview-only early return — every code path from here
        # writes an attempt and may trigger XP / badge / cosmetic unlocks.
        cosmetics_before = owned_slugs(request.user)

        ExerciseAttempt.objects.create(
            student=request.user,
            exercise=exercise,
            answer=answer,
            is_correct=is_correct,
            session_id=session_id,
        )

        # Only a *correct* attempt counts toward the exercise quest —
        # its copy says "Rezolvă corect ...". The view already graded
        # the attempt above.
        if is_correct:
            _safe_record_quest_progress(request.user, "exercise_completed")

        xp_gained = 0
        streak_badges: list[str] = []
        try:
            xp_gained += record_activity(request.user, "exercise")
            streak_badges = evaluate_streak_badges_for(request.user)
        except Exception:
            logger.warning("Streak update failed", exc_info=True)

        # ── Category stats update (atomic, F-expressions) ────────────
        if exercise.category:
            cp_stats, _ = CategoryProgress.objects.get_or_create(
                student=request.user,
                topic=exercise.topic,
                category=exercise.category,
            )
            stats_update = {
                "total_attempts": F("total_attempts") + 1,
                "last_attempted_at": timezone.now(),
            }
            if is_correct:
                stats_update["correct_attempts"] = F("correct_attempts") + 1
            CategoryProgress.objects.filter(pk=cp_stats.pk).update(**stats_update)

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

        if tier_cleared and exercise.category:
            # Tier clears are content-based — route to the content's
            # grade (exercise → topic → unit → grade), not the student's.
            grade = content_grade_for_topic(exercise.topic_id)
            if grade is not None:
                tiers_to_award = [tier_cleared["tier"], *tier_cleared.get("also_cleared", [])]
                for tier in tiers_to_award:
                    try:
                        xp_gained += award_xp(
                            request.user,
                            f"category_{tier}_tier_cleared",
                            {"category_id": exercise.category},
                            grade,
                        )
                    except Exception:
                        logger.warning("XP award failed", exc_info=True)

        correct_display = _correct_answer_display(exercise.exercise_type, grading_data) if not is_correct else None

        own_badges: list[str] = []
        try:
            own_badges = evaluate_badges_for_event(
                request.user, "exercise_attempted", None,
            )
        except Exception:
            logger.warning("Badge evaluation failed", exc_info=True)

        return Response({
            "is_correct": is_correct,
            "correct_answer": correct_display,
            "follow_up": follow_up,
            "tier_cleared": tier_cleared,
            "hint_active_for_category": hint_active_for_category,
            "error": error if not is_correct else None,
            "newly_earned_badges": serialize_badges(streak_badges + own_badges),
            "newly_unlocked_cosmetics": serialize_cosmetics(
                owned_slugs(request.user) - cosmetics_before
            ),
            "xp_gained": xp_gained,
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


# ─── Weak categories ──────────────────────────────────────────────────────────

class WeakCategoriesView(APIView):
    """
    GET /api/v1/progress/weak-categories/?limit=3

    Returns the student's weakest practice categories ranked by lowest
    accuracy. Requires ≥5 attempts per category; excludes cleared
    (medium_cleared=True) categories and empty-category rows.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 3))
        except (TypeError, ValueError):
            limit = 3
        limit = max(1, min(limit, 10))

        rows = list(
            CategoryProgress.objects
            .filter(
                student=request.user,
                total_attempts__gte=5,
                medium_cleared=False,
            )
            .exclude(category="")
            .select_related("topic")
        )

        def _sort_key(cp):
            accuracy = cp.correct_attempts / cp.total_attempts if cp.total_attempts else 0.0
            recency = cp.last_attempted_at.timestamp() if cp.last_attempted_at else 0.0
            return (accuracy, -recency)

        rows.sort(key=_sort_key)
        ranked = rows[:limit]

        results = [
            {
                "category": cp.category,
                "category_label": get_display_name(cp.category),
                "topic_id": cp.topic_id,
                "topic_title": cp.topic.title,
                "accuracy": round(cp.correct_attempts / cp.total_attempts, 2),
                "total_attempts": cp.total_attempts,
                "last_attempted_at": cp.last_attempted_at,
            }
            for cp in ranked
        ]

        return Response({"categories": results})


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

        # Distinct *non-empty* exercise categories per topic. Empty-category
        # rows never appear in CategoryProgress (unique_together excludes
        # them in practice), so excluding them keeps is_perfect honest.
        cat_counts = (
            Exercise.objects
            .filter(topic_id__in=topic_ids, is_active=True)
            .exclude(category="")
            .values("topic_id")
            .annotate(total=Count("category", distinct=True))
        )
        cat_count_map = {row["topic_id"]: row["total"] for row in cat_counts}

        # Per-tier clearance counts per topic, plus the "completed"
        # (medium-or-hard) count used by the existing summary stat.
        completed_by_topic: dict[int, int] = defaultdict(int)
        easy_by_topic: dict[int, int] = defaultdict(int)
        medium_by_topic: dict[int, int] = defaultdict(int)
        hard_by_topic: dict[int, int] = defaultdict(int)
        for cp in CategoryProgress.objects.filter(
            student=user, topic_id__in=topic_ids,
        ).exclude(category=""):
            if cp.medium_cleared or cp.hard_cleared:
                completed_by_topic[cp.topic_id] += 1
            if cp.easy_cleared:
                easy_by_topic[cp.topic_id] += 1
            if cp.medium_cleared:
                medium_by_topic[cp.topic_id] += 1
            if cp.hard_cleared:
                hard_by_topic[cp.topic_id] += 1

        # Exercises attempted per topic
        attempt_count_map: dict[int, int] = {}
        for row in (
            ExerciseAttempt.objects
            .filter(student=user, exercise__topic_id__in=topic_ids)
            .values("exercise__topic_id")
            .annotate(count=Count("id"))
        ):
            attempt_count_map[row["exercise__topic_id"]] = row["count"]

        results = []
        for topic in topics:
            total = cat_count_map.get(topic.id, 0)
            easy_c = easy_by_topic.get(topic.id, 0)
            medium_c = medium_by_topic.get(topic.id, 0)
            hard_c = hard_by_topic.get(topic.id, 0)
            is_perfect = total > 0 and easy_c == total and medium_c == total and hard_c == total
            results.append({
                "topic_id": topic.id,
                "topic_title": topic.title,
                "unit_id": topic.unit_id,
                "unit_title": topic.unit.title,
                "unit_order": topic.unit.order,
                "topic_order": topic.order,
                "total_categories": total,
                "completed_categories": completed_by_topic.get(topic.id, 0),
                "easy_clear_count": easy_c,
                "medium_clear_count": medium_c,
                "hard_clear_count": hard_c,
                "is_perfect": is_perfect,
                "exercises_attempted": attempt_count_map.get(topic.id, 0),
            })

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

        topic_tests = list(
            Test.objects
            .filter(scope=Test.Scope.TOPIC, is_published=True, topic__is_published=True)
            .select_related("topic__unit__grade")
            .order_by("topic__unit__order", "topic__order")
        )
        unit_tests = list(
            Test.objects
            .filter(scope=Test.Scope.UNIT, is_published=True, unit__is_published=True)
            .select_related("unit__grade")
            .order_by("unit__grade__number", "unit__order")
        )
        all_tests = topic_tests + unit_tests
        all_test_ids = [t.id for t in all_tests]

        attempt_stats = (
            TestAttempt.objects
            .filter(
                student=user,
                test_id__in=all_test_ids,
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

        passed_test_ids = get_passed_test_ids(user)
        test_unlock_map = get_test_unlock_map(all_tests, user, passed_test_ids=passed_test_ids)

        def _attempt_fields(test_id: int) -> dict:
            a = attempt_map.get(test_id)
            return {
                "attempts_count": a["attempts_count"] if a else 0,
                "passed": bool(a["passed_count"]) if a else None,
                "best_score": (
                    float(a["best_score"]) if a and a["best_score"] is not None else None
                ),
                "is_locked": not test_unlock_map.get(test_id, True),
            }

        topic_results = [
            {
                "test_id": t.id,
                "topic_id": t.topic_id,
                "topic_title": t.topic.title,
                "unit_id": t.topic.unit_id,
                "unit_title": t.topic.unit.title,
                "unit_order": t.topic.unit.order,
                "topic_order": t.topic.order,
                "pass_threshold": t.pass_threshold,
                "time_limit_minutes": t.time_limit_minutes,
                **_attempt_fields(t.id),
            }
            for t in topic_tests
        ]

        unit_results = [
            {
                "test_id": t.id,
                "unit_id": t.unit_id,
                "unit_title": t.unit.title,
                "unit_order": t.unit.order,
                "pass_threshold": t.pass_threshold,
                "time_limit_minutes": t.time_limit_minutes,
                **_attempt_fields(t.id),
            }
            for t in unit_tests
        ]

        return Response({"tests": topic_results, "unit_tests": unit_results})


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
        from django.db.models.functions import TruncDate

        streak, _ = Streak.objects.get_or_create(student=request.user)

        cutoff = _today_local() - timedelta(days=365)

        # Per-day exercise attempt counts drive heatmap intensity.
        attempt_rows = (
            ExerciseAttempt.objects
            .filter(student=request.user, attempted_at__date__gte=cutoff)
            .annotate(day=TruncDate("attempted_at"))
            .values("day")
            .annotate(count=Count("id"))
        )
        daily_counts: dict[str, int] = {
            row["day"].isoformat(): row["count"] for row in attempt_rows
        }

        # Lesson-only / test-only active days still get a cell at count=1.
        active_dates = StreakActivity.objects.filter(
            student=request.user, date__gte=cutoff,
        ).values_list("date", flat=True)
        for d in active_dates:
            key = d.isoformat()
            if key not in daily_counts:
                daily_counts[key] = 1

        data = {
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "freeze_count": streak.freeze_count,
            "daily_counts": daily_counts,
        }

        serializer = StreakSerializer(data)
        return Response(serializer.data)


# ─── Daily test ───────────────────────────────────────────────────────────────

def _eligible_daily_categories(student) -> list[str]:
    """Categories the student can draw a daily test from.

    Sourced from topics with at least one opened lesson. Prefers medium-
    difficulty categories; falls back to any-difficulty if none exist.
    Caller decides what to do with an empty result.
    """
    opened_topic_ids = list(
        LessonProgress.objects
        .filter(student=student)
        .values_list("lesson__topic_id", flat=True)
        .distinct()
    )

    categories = [
        c for c in (
            Exercise.objects
            .filter(
                topic_id__in=opened_topic_ids,
                is_active=True,
                difficulty="medium",
            )
            .values_list("category", flat=True)
            .distinct()
        ) if c
    ]
    if categories:
        return categories

    return [
        c for c in (
            Exercise.objects
            .filter(topic_id__in=opened_topic_ids, is_active=True)
            .values_list("category", flat=True)
            .distinct()
        ) if c
    ]


def _serialize_session(session: DailyTestSession) -> dict:
    """Serialize a DailyTestSession into the in_progress or completed shape."""
    total = len(session.exercise_instances)
    completed_count = len(session.completed_indices)

    if session.is_completed:
        exercises_with_index = [
            {**instance, "index": idx}
            for idx, instance in enumerate(session.exercise_instances)
        ]
        return {
            "status": "completed",
            "completed_at": session.completed_at,
            "exercise_count": total,
            "completed_count": completed_count,
            "exercises": exercises_with_index,
            "completed_indices": list(session.completed_indices),
            "answers": dict(session.answers or {}),
        }

    completed_set = set(session.completed_indices)
    pending = [
        {**instance, "index": idx}
        for idx, instance in enumerate(session.exercise_instances)
        if idx not in completed_set
    ]
    return {
        "status": "in_progress",
        "exercises": pending,
        "completed_count": completed_count,
        "total_count": total,
    }


class DailyTestView(APIView):
    """
    GET /api/v1/progress/daily/

    Read-only status check. Returns the existing session if one was
    started today, otherwise reports whether a new test is available
    based on the student's eligible category pool. Does NOT create
    a session — start it with POST /daily/start/.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = _today_local()
        session = DailyTestSession.objects.filter(
            student=request.user, date=today
        ).first()

        if session is not None:
            return Response(_serialize_session(session))

        categories = _eligible_daily_categories(request.user)
        if not categories:
            return Response({
                "status": "no_exercises",
                "message": (
                    "Deschide câteva lecții și exersează puțin înainte de "
                    "a primi un test zilnic."
                ),
            })

        return Response({
            "status": "available",
            "exercise_count": 5,
        })


class DailyTestStartView(APIView):
    """
    POST /api/v1/progress/daily/start/

    Creates today's DailyTestSession if one doesn't already exist, then
    returns the session state. Idempotent — re-calling just returns the
    existing session.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        import random

        today = _today_local()
        session = DailyTestSession.objects.filter(
            student=request.user, date=today
        ).first()

        if session is not None:
            return Response(_serialize_session(session))

        categories = _eligible_daily_categories(request.user)
        if not categories:
            return Response({
                "status": "no_exercises",
                "message": (
                    "Deschide câteva lecții și exersează puțin înainte de "
                    "a primi un test zilnic."
                ),
            })

        shuffled = random.sample(categories, len(categories))
        slot_categories = list(shuffled[:5])
        while len(slot_categories) < 5:
            slot_categories.append(shuffled[len(slot_categories) % len(shuffled)])

        instances: list[dict] = []
        for cat in slot_categories:
            ex = (
                Exercise.objects
                .filter(category=cat, difficulty="medium", is_active=True)
                .order_by("?")
                .first()
            )
            if ex is None:
                ex = (
                    Exercise.objects
                    .filter(category=cat, difficulty="easy", is_active=True)
                    .order_by("?")
                    .first()
                )
            if ex is None:
                continue
            try:
                instance = generate_instance(ex)
                instance["exercise_id"] = ex.id
                instances.append(instance)
            except Exception:
                continue

        if not instances:
            return Response({
                "status": "no_exercises",
                "message": (
                    "Nu există exerciții disponibile pentru testul zilnic de azi."
                ),
            })

        session = DailyTestSession.objects.create(
            student=request.user,
            date=today,
            exercise_instances=instances,
            completed_indices=[],
        )

        # Fired only on the creation path — the early return above
        # handles the idempotent "already started" case.
        _safe_record_quest_progress(request.user, "daily_test_started")

        return Response(_serialize_session(session))


class DailyTestSubmitView(APIView):
    """
    POST /api/v1/progress/daily/submit/

    Body: {"answers": {"0": <answer>, "3": <answer>}}

    Grades each submitted answer. Correct indices are marked complete;
    wrong (or expired) slots have their instance regenerated with fresh
    params so the student can retry.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        today = _today_local()
        session = DailyTestSession.objects.filter(
            student=request.user, date=today
        ).first()

        if session is None:
            return Response(
                {"error": "Nu există un test zilnic activ."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if session.is_completed:
            total = len(session.exercise_instances)
            return Response({
                "results": {},
                "is_completed": True,
                "completed_count": len(session.completed_indices),
                "total_count": total,
                "pending_exercises": [],
            })

        # Snapshot owned cosmetics for the post-request diff. The
        # completion path below grants streak XP and a streak badge cascade,
        # both of which may unlock cosmetics.
        cosmetics_before = owned_slugs(request.user)

        raw_answers = request.data.get("answers") or {}
        if not isinstance(raw_answers, dict):
            return Response(
                {"error": "Câmpul answers trebuie să fie un obiect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instances = list(session.exercise_instances)
        completed_set = set(session.completed_indices)
        results: dict[str, dict] = {}
        regenerated_pending: list[dict] = []

        for key, student_answer in raw_answers.items():
            try:
                idx = int(key)
            except (TypeError, ValueError):
                continue
            if idx < 0 or idx >= len(instances) or idx in completed_set:
                continue

            instance = instances[idx]
            exercise_id = instance.get("exercise_id")
            instance_token = instance.get("instance_token")

            try:
                exercise = Exercise.objects.select_related("topic").get(id=exercise_id)
            except Exercise.DoesNotExist:
                continue

            is_correct = False
            correct_display = None

            try:
                payload = decode_instance_token(instance_token, max_age=None)
                grading_data = payload.get("grading_data", payload)
                is_correct, _ = grade_attempt(
                    exercise.exercise_type, student_answer, grading_data,
                )
                if not is_correct:
                    correct_display = _correct_answer_display(
                        exercise.exercise_type, grading_data,
                    )
            except Exception:
                pass

            if is_correct:
                completed_set.add(idx)
                session.answers[str(idx)] = student_answer
                results[str(idx)] = {"is_correct": True, "correct_answer": None}
                continue

            try:
                new_instance = generate_instance(exercise)
                new_instance["exercise_id"] = exercise.id
            except Exception:
                new_instance = instance
            instances[idx] = new_instance

            results[str(idx)] = {
                "is_correct": False,
                "correct_answer": correct_display,
            }
            regenerated_pending.append({**new_instance, "index": idx})

        session.exercise_instances = instances
        session.completed_indices = sorted(completed_set)

        total = len(instances)
        xp_gained = 0
        streak_badges: list[str] = []
        if total > 0 and len(completed_set) == total:
            session.is_completed = True
            session.completed_at = timezone.now()
            session.save()
            _safe_record_quest_progress(request.user, "daily_test_completed")
            try:
                xp_gained += record_activity(request.user, "daily_test")
                streak_badges = evaluate_streak_badges_for(request.user)
            except Exception:
                logger.warning("Streak update failed", exc_info=True)
            # No direct XP here — the daily loop's XP now comes from the
            # daily-test quests (started/completed/passed) and the
            # milestone bar, not a `daily_test_complete` grant.
        else:
            session.save(update_fields=["exercise_instances", "completed_indices", "answers"])

        return Response({
            "results": results,
            "is_completed": session.is_completed,
            "completed_count": len(session.completed_indices),
            "total_count": total,
            "pending_exercises": regenerated_pending,
            "newly_earned_badges": serialize_badges(streak_badges),
            "newly_unlocked_cosmetics": serialize_cosmetics(
                owned_slugs(request.user) - cosmetics_before
            ),
            "xp_gained": xp_gained,
        })


# ─── Test session views ───────────────────────────────────────────────────────

class TestStartView(APIView):
    """POST /api/v1/progress/tests/<test_id>/start/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, test_id):
        try:
            test = Test.objects.get(id=test_id, is_published=True)
        except Test.DoesNotExist:
            return Response({"error": "Testul nu există."}, status=status.HTTP_404_NOT_FOUND)

        passed_test_ids = get_passed_test_ids(request.user)
        if not is_test_unlocked(test, passed_test_ids):
            return Response(
                {"error": "Testul nu este disponibil încă.", "locked": True},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Reuse existing in-progress attempt if any — but abandon stale ones
        # whose instance tokens may have expired (1-hour default signing TTL,
        # so a 24-hour staleness threshold is safely past that window).
        attempt = TestAttempt.objects.filter(
            student=request.user,
            test=test,
            status=TestAttempt.Status.IN_PROGRESS,
        ).first()

        if attempt and timezone.now() - attempt.started_at > timedelta(hours=24):
            attempt.status = TestAttempt.Status.ABANDONED
            attempt.save(update_fields=["status"])
            attempt = None

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

        # Snapshot owned cosmetics for the post-request diff — the
        # finish path grants streak/test-passed XP and fires the badge
        # evaluator, either of which may unlock cosmetics.
        cosmetics_before = owned_slugs(request.user)

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

            correct_display = None
            try:
                exercise = Exercise.objects.get(id=exercise_id)
                payload = decode_instance_token(instance_token, max_age=None)
                grading_data = payload.get("grading_data", payload)
                is_correct, _ = grade_attempt(
                    exercise.exercise_type, student_answer, grading_data
                )
                if not is_correct:
                    correct_display = _correct_answer_display(
                        exercise.exercise_type, grading_data,
                    )
            except Exception:
                is_correct = False

            if is_correct:
                earned_weight += weight

            graded_answers[str_idx] = {
                "answer": student_answer,
                "is_correct": is_correct,
                "correct_answer": correct_display,
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

        xp_gained = 0
        streak_badges: list[str] = []
        try:
            act_type = "topic_test" if test.scope == "topic" else "unit_test"
            xp_gained += record_activity(request.user, act_type)
            streak_badges = evaluate_streak_badges_for(request.user)
        except Exception:
            logger.warning("Streak update failed", exc_info=True)

        if passed:
            _safe_record_quest_progress(request.user, "test_passed")
            try:
                xp_gained += _award_test_passed_xp(request.user, attempt)
            except Exception:
                logger.warning("XP award failed", exc_info=True)

        own_badges: list[str] = []
        try:
            own_badges = evaluate_badges_for_event(
                request.user, "test_finished", {"test_attempt": attempt},
            )
        except Exception:
            logger.warning("Badge evaluation failed", exc_info=True)

        return Response({
            "attempt_id": attempt.id,
            "score": round(score, 2),
            "passed": passed,
            "pass_threshold": test.pass_threshold,
            "answers": graded_answers,
            "newly_earned_badges": serialize_badges(streak_badges + own_badges),
            "newly_unlocked_cosmetics": serialize_cosmetics(
                owned_slugs(request.user) - cosmetics_before
            ),
            "xp_gained": xp_gained,
        })


class TestHistoryView(APIView):
    """
    GET /api/v1/progress/test-history/?limit=20

    Returns completed test attempts for the authenticated student, newest first.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 20))
        except (TypeError, ValueError):
            limit = 20
        limit = max(1, min(limit, 50))

        attempts = (
            TestAttempt.objects
            .filter(student=request.user, status=TestAttempt.Status.COMPLETED)
            .select_related("test__topic", "test__unit")
            .order_by("-finished_at")[:limit]
        )

        results = []
        for a in attempts:
            test = a.test
            if test.scope == Test.Scope.TOPIC:
                title = test.topic.title if test.topic else ""
            else:
                title = test.unit.title if test.unit else ""
            results.append({
                "attempt_id": a.id,
                "test_id": test.id,
                "test_scope": test.scope,
                "test_title": title,
                "score": float(a.score) if a.score is not None else None,
                "passed": a.passed,
                "pass_threshold": test.pass_threshold,
                "started_at": a.started_at,
                "finished_at": a.finished_at,
                "exercise_count": len(a.exercise_instances or []),
            })

        return Response({"attempts": results})


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
            "exercise_instances": attempt.exercise_instances,
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
                instance["topic_id"] = ex.topic_id
                instance["category_label"] = get_display_name(ex.category)
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


# ─── Achievements ─────────────────────────────────────────────────────────────

class AchievementListView(APIView):
    """
    GET /api/v1/progress/achievements/

    Catalog-shaped list of every badge with the student's earned state.
    Secret badges that haven't been earned yet are returned with name,
    description, and icon_name nulled so the frontend can render the
    mystery placeholder.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.progress.badges.catalog import CATALOG
        from apps.progress.models import Achievement

        user = request.user
        if not getattr(user, "is_student", False):
            return Response(
                {"error": "Doar elevii au insigne."},
                status=status.HTTP_403_FORBIDDEN,
            )

        earned_at_by_key = dict(
            Achievement.objects
            .filter(student=user)
            .values_list("badge_key", "earned_at")
        )

        achievements = []
        for badge in CATALOG.values():
            earned_at = earned_at_by_key.get(badge.key)
            earned = earned_at is not None
            hidden = badge.secret and not earned
            achievements.append({
                "key": badge.key,
                "family": badge.family,
                "secret": badge.secret,
                "earned": earned,
                "earned_at": earned_at.isoformat() if earned_at else None,
                "name": None if hidden else badge.name,
                "description": None if hidden else badge.description,
                "icon_name": None if hidden else badge.icon_name,
            })

        return Response({"achievements": achievements})


# ─── Cosmetics ────────────────────────────────────────────────────────────────

class CosmeticListView(APIView):
    """
    GET /api/v1/progress/cosmetics/

    Catalog-shaped list of every cosmetic with the student's owned and
    equipped state. For locked entries it includes a displayable unlock
    requirement: xp_threshold carries its number, while achievement and
    quest_reward conditions are resolved to the badge's display name /
    quest's title via runtime catalog lookups. Also returns the
    currently-equipped cosmetic per type and the profile's
    `avatar_source` so the frontend can render the active look without a
    second call.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not getattr(request.user, "is_student", False):
            return Response(
                {"error": "Doar elevii au cosmetice."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(build_catalog_state(request.user))


class CosmeticEquipView(APIView):
    """
    POST /api/v1/progress/cosmetics/<slug>/equip/

    Equips a cosmetic the student owns. Rejected with 404 on an unknown
    slug and 403 on a not-owned cosmetic. The one-equipped-per-type
    invariant is held transactionally — the existing equipped cosmetic
    of the same type is cleared first, then the target is set — so the
    `uniq_one_equipped_per_type` partial index can never reject. An
    avatar equip also flips `avatar_source` to PRESET on the profile so
    the displayed avatar actually resolves to the preset.

    Returns the post-equip equipped snapshot and avatar_source — the
    same shape the list endpoint exposes.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        if not getattr(request.user, "is_student", False):
            return Response(
                {"error": "Doar elevii pot echipa cosmetice."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            data = equip_cosmetic(request.user, slug)
        except CosmeticEquipError as exc:
            return Response({"error": exc.message}, status=exc.status_code)
        return Response(data)


class AvatarUploadView(APIView):
    """
    POST /api/v1/progress/avatar/upload/   (multipart, field `avatar`)

    Validates the uploaded file as an actual image (Pillow, never the
    Content-Type header), enforces a 5 MB cap, guards against
    decompression-bomb dimensions, then normalises every accepted
    upload: EXIF orientation applied, center-cropped to a 256×256
    square, metadata stripped, re-encoded to JPEG. Saved under a
    UUID-named file (never the student's original name); replaces any
    previously-stored avatar. On success `avatar_source` is flipped to
    UPLOAD and the post-upload avatar block is returned (the same shape
    surfaced by the list/equip endpoints). Corrupt / non-image / too-
    large input yields a clean 400.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not getattr(request.user, "is_student", False):
            return Response(
                {"error": "Doar elevii pot încărca avatare."},
                status=status.HTTP_403_FORBIDDEN,
            )
        uploaded = request.FILES.get("avatar")
        if uploaded is None:
            return Response(
                {"error": "Câmpul 'avatar' este obligatoriu."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            data = upload_avatar(request.user, uploaded)
        except InvalidAvatarUpload as exc:
            # The pipeline's own Romanian message is the user-facing reason.
            return Response(
                {"error": exc.message_ro},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except AvatarSourceError as exc:
            return Response({"error": exc.message}, status=exc.status_code)
        return Response(data)


class AvatarSourceView(APIView):
    """
    POST /api/v1/progress/avatar/source/   body: {"source": "monogram"|"upload"|"preset"}

    Sets which of the three sources the displayed avatar resolves from.
    MONOGRAM is always reachable; UPLOAD requires a stored image;
    PRESET requires an equipped avatar-type cosmetic (note that
    equipping such a cosmetic already flips the source to PRESET in
    CosmeticEquipView, so this endpoint mainly covers moving back to
    MONOGRAM or to an existing UPLOAD). Returns the post-switch avatar
    block — the same shape surfaced everywhere else.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not getattr(request.user, "is_student", False):
            return Response(
                {"error": "Doar elevii au sursă de avatar."},
                status=status.HTTP_403_FORBIDDEN,
            )
        source = request.data.get("source")
        if not isinstance(source, str):
            return Response(
                {"error": "Câmpul 'source' este obligatoriu."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            data = set_avatar_source(request.user, source)
        except AvatarSourceError as exc:
            return Response({"error": exc.message}, status=exc.status_code)
        return Response(data)


# ─── XP ledger ────────────────────────────────────────────────────────────────

class _XPLedgerPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = None
    max_page_size = 50


class XPLedgerView(APIView):
    """
    GET /api/v1/progress/xp/ledger/?grade=<N>&page=<N>

    Paginated list of the student's XP grants, newest first. Optional
    `grade` query param filters to a specific grade-numbered ledger
    (i.e. one pet's lifetime). Each row carries a Romanian
    `source_display` resolved from the XP_AWARDS catalog.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.progress.xp import XPLedger
        from apps.progress.xp.awards import XP_AWARDS

        user = request.user
        if not getattr(user, "is_student", False):
            return Response(
                {"error": "Doar elevii au istoric XP."},
                status=status.HTTP_403_FORBIDDEN,
            )

        qs = (
            XPLedger.objects
            .filter(student=user)
            .select_related("grade")
            .order_by("-granted_at", "-id")
        )

        grade_param = request.query_params.get("grade")
        if grade_param is not None:
            try:
                grade_number = int(grade_param)
            except (TypeError, ValueError):
                return Response(
                    {"error": "Parametrul grade trebuie să fie un număr."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            qs = qs.filter(grade__number=grade_number)

        paginator = _XPLedgerPagination()
        page = paginator.paginate_queryset(qs, request, view=self)

        rows = [
            {
                "source": row.source,
                "source_display": (
                    XP_AWARDS[row.source]["display_name"]
                    if row.source in XP_AWARDS else row.source
                ),
                "amount": row.amount,
                "granted_at": row.granted_at.isoformat(),
                "grade_number": row.grade.number,
            }
            for row in page
        ]
        return paginator.get_paginated_response(rows)


# ─── Quests ───────────────────────────────────────────────────────────────────

class QuestSyncView(APIView):
    """
    POST /api/v1/progress/quests/sync/

    Idempotently materialises the student's current-period quest state
    (one assignment per daily catalog entry at today's daily period
    key, one per weekly entry at this week's weekly key, plus today's
    points-bar row), emits the generic `login` event, and returns the
    full current-period state. Re-calling is a no-op beyond the login
    tick. No claim / payout here — that is Phase 3.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from apps.progress.quests.service import sync_quests

        if not getattr(request.user, "is_student", False):
            return Response(
                {"error": "Doar elevii au misiuni."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(sync_quests(request.user))


class QuestListView(APIView):
    """
    GET /api/v1/progress/quests/

    Read-only current-period quest state: daily and weekly assignments
    enriched with their catalog title/description, plus the daily
    points bar. Bulk queries only; never creates rows (POST
    /quests/sync/ is the only writer).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.progress.quests.service import build_current_period_state

        if not getattr(request.user, "is_student", False):
            return Response(
                {"error": "Doar elevii au misiuni."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(build_current_period_state(request.user))


class QuestClaimView(APIView):
    """
    POST /api/v1/progress/quests/<assignment_id>/claim/

    Claims a completed quest: status → claimed, the catalog xp_reward
    is paid into the student's current-grade pet, and a daily quest
    also accrues its point_value to today's bar. Returns the updated
    assignment (+ bar for a daily claim) and surfaces `xp_gained` per
    the Block 10 XP-toast convention.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, assignment_id):
        from apps.progress.quests.service import QuestClaimError, claim_quest

        if not getattr(request.user, "is_student", False):
            return Response(
                {"error": "Doar elevii au misiuni."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Snapshot owned cosmetics for the post-request diff. A claim
        # may unlock a quest_reward cosmetic directly (the claim's
        # post-commit hook) and the paid xp_reward may cross an
        # xp_threshold (via award_xp's own post-commit hook); the diff
        # catches both uniformly.
        cosmetics_before = owned_slugs(request.user)

        try:
            data = claim_quest(request.user, assignment_id)
        except QuestClaimError as exc:
            return Response({"error": exc.message}, status=exc.status_code)

        # A claimed daily quest feeds the weekly "claim N dailies" quest.
        # Post-commit, defensive (Block 10 cross-system-hook convention).
        if data["assignment"]["cadence"] == "daily":
            _safe_record_quest_progress(request.user, "daily_quest_claimed")

        data["newly_unlocked_cosmetics"] = serialize_cosmetics(
            owned_slugs(request.user) - cosmetics_before
        )
        return Response(data)


class MilestoneClaimView(APIView):
    """
    POST /api/v1/progress/quests/milestone/<threshold>/claim/

    Claims a daily points-bar milestone rung: records the threshold and
    pays its DAILY_MILESTONES XP into the student's current-grade pet.
    Returns the updated bar and surfaces `xp_gained`.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, threshold):
        from apps.progress.quests.service import (
            QuestClaimError,
            claim_milestone,
        )

        if not getattr(request.user, "is_student", False):
            return Response(
                {"error": "Doar elevii au misiuni."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            data = claim_milestone(request.user, threshold)
        except QuestClaimError as exc:
            return Response({"error": exc.message}, status=exc.status_code)
        return Response(data)
