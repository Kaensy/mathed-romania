"""End-to-end tests for Block 10 Phase 2 view wiring.

Each test class exercises one of the five wiring sites and verifies:
  (a) the right XP source(s) fire on the intended trigger
  (b) idempotency holds end-to-end (no double-award on repeated calls)
  (c) the response's `xp_gained` matches actual ledger writes for that
      request
"""
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.content.models import Exercise, Grade, Lesson, Test, Topic, Unit
from apps.progress.exercise_engine import generate_instance
from apps.progress.models import (
    CategoryProgress,
    DailyTestSession,
    LessonProgress,
    TestAttempt,
)
from apps.progress.streak_service import _today_local
from apps.progress.xp import XPLedger
from apps.users.models import StudentProfile

User = get_user_model()


def _make_student(grade_number=5, *, email="alice@example.com"):
    user = User.objects.create_user(
        email=email, password="x", user_type="student",
        first_name="Alice", last_name="A",
    )
    StudentProfile.objects.create(
        user=user, grade=grade_number, birth_date=date(2014, 1, 1),
    )
    return user


def _content_skeleton(grade_number=5):
    grade = Grade.objects.create(number=grade_number, name=f"Clasa {grade_number}")
    unit = Unit.objects.create(
        grade=grade, order=1, title="U1", is_published=True,
    )
    topic = Topic.objects.create(
        unit=unit, order=1, title="T1", is_published=True,
    )
    lesson = Lesson.objects.create(
        topic=topic, order=1, title="L1", blocks=[], is_published=True,
    )
    return grade, unit, topic, lesson


def _simple_fill_blank_exercise(topic, *, category="addition_compute", difficulty="easy"):
    return Exercise.objects.create(
        topic=topic,
        exercise_type="fill_blank",
        difficulty=difficulty,
        category=category,
        template={
            "type": "fill_blank",
            "question": "Calculați: {a} + {b}",
            "params": {
                "a": {"type": "fixed", "value": 2},
                "b": {"type": "fixed", "value": 3},
            },
            "answer_expr": "{a} + {b}",
            "answer_input": "number",
        },
        is_active=True,
    )


# ─── Site 1+3: LessonOpenView ────────────────────────────────────────────────

class LessonOpenWiringTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grade, _, _, cls.lesson = _content_skeleton()
        cls.student = _make_student()

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.student)

    def test_first_open_fires_lesson_first_open_and_daily_first_login(self):
        url = reverse("lesson_open", args=[self.lesson.id])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

        sources = set(XPLedger.objects.values_list("source", flat=True))
        self.assertIn("lesson_first_open", sources)
        self.assertIn("daily_first_login", sources)

        ledger_total = sum(XPLedger.objects.values_list("amount", flat=True))
        self.assertEqual(resp.data["xp_gained"], ledger_total)
        self.assertGreater(resp.data["xp_gained"], 0)

    def test_revisit_does_not_re_award(self):
        url = reverse("lesson_open", args=[self.lesson.id])
        first = self.client.post(url)
        ledger_after_first = list(
            XPLedger.objects.values_list("source", "idempotency_key")
        )

        second = self.client.post(url)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.data["xp_gained"], 0)
        ledger_after_second = list(
            XPLedger.objects.values_list("source", "idempotency_key")
        )
        self.assertEqual(ledger_after_first, ledger_after_second)

    def test_xp_gained_matches_ledger_writes_for_request(self):
        url = reverse("lesson_open", args=[self.lesson.id])
        before = XPLedger.objects.count()
        resp = self.client.post(url)
        after = XPLedger.objects.count()
        new_rows = XPLedger.objects.order_by("-granted_at")[: after - before]
        self.assertEqual(
            resp.data["xp_gained"], sum(r.amount for r in new_rows),
        )


# ─── Site 2: ExerciseAttemptView ─────────────────────────────────────────────

class ExerciseAttemptWiringTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grade, _, cls.topic, _ = _content_skeleton()
        cls.exercise = _simple_fill_blank_exercise(cls.topic)
        cls.student = _make_student()

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.student)

    def _attempt(self, *, correct: bool, session_id=None):
        instance = generate_instance(self.exercise)
        payload = {
            "exercise_id": self.exercise.id,
            "instance_token": instance["instance_token"],
            "answer": "5" if correct else "999",
        }
        if session_id is not None:
            payload["session_id"] = str(session_id)
        return self.client.post(
            reverse("exercise_attempt"), payload, format="json",
        )

    def test_first_correct_attempt_fires_try_and_complete_and_login(self):
        resp = self._attempt(correct=True)
        self.assertEqual(resp.status_code, 200)
        sources = set(XPLedger.objects.values_list("source", flat=True))
        self.assertEqual(
            sources,
            {"daily_first_login", "daily_first_exercise_try", "daily_first_exercise_complete"},
        )
        self.assertEqual(
            resp.data["xp_gained"],
            sum(XPLedger.objects.values_list("amount", flat=True)),
        )

    def test_first_wrong_attempt_only_fires_try(self):
        resp = self._attempt(correct=False)
        self.assertEqual(resp.status_code, 200)
        sources = set(XPLedger.objects.values_list("source", flat=True))
        self.assertIn("daily_first_exercise_try", sources)
        self.assertNotIn("daily_first_exercise_complete", sources)
        self.assertEqual(
            resp.data["xp_gained"],
            sum(XPLedger.objects.values_list("amount", flat=True)),
        )

    def test_repeated_attempts_same_day_dont_re_award(self):
        first = self._attempt(correct=True)
        rows_after_first = XPLedger.objects.count()
        second = self._attempt(correct=True)
        self.assertEqual(second.data["xp_gained"], 0)
        self.assertEqual(XPLedger.objects.count(), rows_after_first)

    def test_clearing_easy_tier_awards_category_easy_tier_cleared(self):
        import uuid
        session_id = uuid.uuid4()
        for _ in range(5):
            self._attempt(correct=True, session_id=session_id)

        rows = list(XPLedger.objects.filter(source="category_easy_tier_cleared"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0].idempotency_key,
            f"category_easy_tier_cleared:cat_{self.exercise.category}",
        )


# ─── Site 4: TestFinishView ──────────────────────────────────────────────────

class TestFinishWiringTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grade, cls.unit, cls.topic, _ = _content_skeleton()
        cls.exercise = _simple_fill_blank_exercise(cls.topic)
        cls.student = _make_student()
        cls.topic_test = Test.objects.create(
            scope="topic", topic=cls.topic, is_published=True,
            composition=[{"category": cls.exercise.category, "count": 1, "weight": 100, "difficulty": "easy"}],
            pass_threshold=60,
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.student)

    def _start_and_answer(self, *, correct: bool):
        instance = generate_instance(self.exercise)
        attempt = TestAttempt.objects.create(
            student=self.student,
            test=self.topic_test,
            exercise_instances=[{**instance, "weight": 100}],
            status=TestAttempt.Status.IN_PROGRESS,
            answers={
                "0": {
                    "answer": "5" if correct else "999",
                    "is_correct": None,
                    "exercise_id": self.exercise.id,
                },
            },
        )
        return attempt

    def test_passed_topic_test_fires_topic_passed(self):
        self._start_and_answer(correct=True)
        resp = self.client.post(
            reverse("test_finish", args=[self.topic_test.id]),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data["passed"])
        sources = set(XPLedger.objects.values_list("source", flat=True))
        self.assertIn("topic_passed", sources)
        self.assertEqual(
            resp.data["xp_gained"],
            sum(XPLedger.objects.values_list("amount", flat=True)),
        )

    def test_passed_with_medium_cleared_also_fires_topic_mastered(self):
        # Pre-clear medium tier for the topic's only category.
        CategoryProgress.objects.create(
            student=self.student, topic=self.topic,
            category=self.exercise.category, medium_cleared=True,
        )
        self._start_and_answer(correct=True)
        resp = self.client.post(
            reverse("test_finish", args=[self.topic_test.id]),
        )
        sources = set(
            XPLedger.objects.values_list("source", flat=True)
        )
        self.assertEqual(
            sources & {"topic_passed", "topic_mastered"},
            {"topic_passed", "topic_mastered"},
        )

    def test_failed_topic_test_does_not_fire_topic_passed(self):
        self._start_and_answer(correct=False)
        resp = self.client.post(
            reverse("test_finish", args=[self.topic_test.id]),
        )
        self.assertFalse(resp.data["passed"])
        sources = set(XPLedger.objects.values_list("source", flat=True))
        self.assertNotIn("topic_passed", sources)

    def test_unit_test_passed_fires_unit_passed(self):
        unit_test = Test.objects.create(
            scope="unit", unit=self.unit, is_published=True,
            composition=[{"category": self.exercise.category, "count": 1, "weight": 100, "difficulty": "easy"}],
            pass_threshold=60,
        )
        instance = generate_instance(self.exercise)
        TestAttempt.objects.create(
            student=self.student,
            test=unit_test,
            exercise_instances=[{**instance, "weight": 100}],
            status=TestAttempt.Status.IN_PROGRESS,
            answers={
                "0": {"answer": "5", "is_correct": None, "exercise_id": self.exercise.id},
            },
        )
        resp = self.client.post(reverse("test_finish", args=[unit_test.id]))
        sources = set(XPLedger.objects.values_list("source", flat=True))
        self.assertIn("unit_passed", sources)
        self.assertEqual(
            resp.data["xp_gained"],
            sum(XPLedger.objects.values_list("amount", flat=True)),
        )


# ─── Site 5: DailyTestSubmitView ─────────────────────────────────────────────

class DailyTestSubmitWiringTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grade, _, cls.topic, _ = _content_skeleton()
        cls.exercise = _simple_fill_blank_exercise(cls.topic)
        cls.student = _make_student()

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.student)

    def _seed_session(self, *, n_correct: int, n_total: int = 2):
        instances = []
        for _ in range(n_total):
            instances.append(generate_instance(self.exercise))
        # Seed answers/completed_indices for the n_correct already-correct slots.
        completed_indices = list(range(n_correct))
        answers = {str(i): "5" for i in range(n_correct)}
        return DailyTestSession.objects.create(
            student=self.student,
            date=_today_local(),
            exercise_instances=instances,
            completed_indices=completed_indices,
            answers=answers,
        )

    def test_completing_last_exercise_fires_daily_test_complete(self):
        session = self._seed_session(n_correct=1, n_total=2)
        resp = self.client.post(
            reverse("daily_test_submit"),
            {"answers": {"1": "5"}},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data["is_completed"])
        sources = set(XPLedger.objects.values_list("source", flat=True))
        self.assertIn("daily_test_complete", sources)
        self.assertEqual(
            resp.data["xp_gained"],
            sum(XPLedger.objects.values_list("amount", flat=True)),
        )

    def test_partial_submission_does_not_fire_daily_test_complete(self):
        self._seed_session(n_correct=0, n_total=2)
        resp = self.client.post(
            reverse("daily_test_submit"),
            {"answers": {"0": "5"}},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data["is_completed"])
        sources = set(XPLedger.objects.values_list("source", flat=True))
        self.assertNotIn("daily_test_complete", sources)

    def test_idempotent_completion(self):
        # Build a fresh single-slot session, complete it twice.
        instance = generate_instance(self.exercise)
        DailyTestSession.objects.create(
            student=self.student, date=_today_local(),
            exercise_instances=[instance],
            completed_indices=[],
            answers={},
        )
        first = self.client.post(
            reverse("daily_test_submit"),
            {"answers": {"0": "5"}},
            format="json",
        )
        first_xp = first.data["xp_gained"]
        rows_after_first = XPLedger.objects.count()

        second = self.client.post(
            reverse("daily_test_submit"),
            {"answers": {"0": "5"}},
            format="json",
        )
        # The session is already_completed branch returns no xp_gained key
        # because the early-return path does not hit the award block.
        # Either way, ledger must not grow.
        self.assertEqual(XPLedger.objects.count(), rows_after_first)
        self.assertGreater(first_xp, 0)
