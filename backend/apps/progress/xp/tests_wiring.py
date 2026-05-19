"""End-to-end tests for the XP/quest view wiring.

Each test class exercises one of the wiring sites and verifies:
  (a) the right XP source(s) fire (or, post Block-11 correction, that a
      retired source no longer fires) on the intended trigger
  (b) idempotency holds end-to-end (no double-award on repeated calls)
  (c) the response's `xp_gained` matches actual ledger writes for that
      request

The four daily_* XP sources were retired in the Block 11 XP-correction
patch (the daily loop's XP now comes from quest claims + the milestone
bar), so several cases below assert their *absence* instead.
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
    QuestAssignment,
    TestAttempt,
)
from apps.progress.quests.service import sync_quests
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

    def test_first_open_fires_only_lesson_first_open(self):
        # daily_first_login was retired — lesson_first_open is the only
        # XP source on a first lesson open now.
        url = reverse("lesson_open", args=[self.lesson.id])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

        sources = set(XPLedger.objects.values_list("source", flat=True))
        self.assertEqual(sources, {"lesson_first_open"})

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

    def _daily_exercise_assignment(self):
        return QuestAssignment.objects.get(
            student__user=self.student, quest_slug="daily_exercise",
        )

    def test_plain_correct_attempt_writes_no_xp(self):
        # The daily_first_exercise_* sources were retired and there is no
        # session, so a lone correct attempt grants no XP.
        resp = self._attempt(correct=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(XPLedger.objects.exists())
        self.assertEqual(resp.data["xp_gained"], 0)

    def test_plain_wrong_attempt_writes_no_xp(self):
        resp = self._attempt(correct=False)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(XPLedger.objects.exists())
        self.assertEqual(resp.data["xp_gained"], 0)

    def test_exercise_quest_only_advances_on_a_correct_attempt(self):
        # Materialise this student's current-period quests, then verify
        # the exercise_completed event is gated on correctness.
        sync_quests(self.student)
        self.assertEqual(self._daily_exercise_assignment().progress, 0)

        self._attempt(correct=False)
        self.assertEqual(self._daily_exercise_assignment().progress, 0)

        self._attempt(correct=True)
        a = self._daily_exercise_assignment()
        self.assertEqual(a.progress, 1)
        self.assertEqual(a.status, QuestAssignment.Status.COMPLETED)

    def test_repeated_attempts_same_day_dont_award_xp(self):
        first = self._attempt(correct=True)
        second = self._attempt(correct=True)
        self.assertEqual(first.data["xp_gained"], 0)
        self.assertEqual(second.data["xp_gained"], 0)
        self.assertFalse(XPLedger.objects.exists())

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

    def test_completing_last_exercise_writes_no_xp(self):
        # daily_test_complete was retired — finishing the daily test
        # still flips is_completed but grants no direct XP.
        self._seed_session(n_correct=1, n_total=2)
        resp = self.client.post(
            reverse("daily_test_submit"),
            {"answers": {"1": "5"}},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data["is_completed"])
        self.assertFalse(XPLedger.objects.exists())
        self.assertEqual(resp.data["xp_gained"], 0)

    def test_partial_submission_does_not_complete_or_award(self):
        self._seed_session(n_correct=0, n_total=2)
        resp = self.client.post(
            reverse("daily_test_submit"),
            {"answers": {"0": "5"}},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data["is_completed"])
        self.assertFalse(XPLedger.objects.exists())

    def test_idempotent_completion_never_writes_xp(self):
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
        self.assertTrue(first.data["is_completed"])
        self.assertEqual(first.data["xp_gained"], 0)

        # Second call hits the already-completed early return (no
        # xp_gained key). Either way, the ledger stays empty.
        self.client.post(
            reverse("daily_test_submit"),
            {"answers": {"0": "5"}},
            format="json",
        )
        self.assertFalse(XPLedger.objects.exists())
