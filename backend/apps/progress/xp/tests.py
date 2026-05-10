"""Tests for the XP foundation: ledger model + award_xp helper."""
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.content.models import Grade
from apps.progress.xp import XP_AWARDS, XPLedger, award_xp
from apps.users.models import StudentProfile

User = get_user_model()


class AwardXPTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grade = Grade.objects.create(number=5, name="Clasa a V-a")
        cls.student = User.objects.create_user(
            email="alice@example.com",
            password="x",
            user_type="student",
            first_name="Alice",
            last_name="A",
        )
        cls.profile = StudentProfile.objects.create(
            user=cls.student,
            grade=5,
            birth_date=date(2014, 1, 1),
        )

    def _refresh_profile(self):
        self.profile.refresh_from_db()
        return self.profile

    # ── happy path ────────────────────────────────────────────────────
    def test_first_grant_returns_amount_and_writes_ledger_row(self):
        amount = award_xp(
            self.student,
            "lesson_first_open",
            {"lesson_id": 42},
            self.grade,
        )
        expected = XP_AWARDS["lesson_first_open"]["amount"]
        self.assertEqual(amount, expected)
        self.assertEqual(XPLedger.objects.count(), 1)

        row = XPLedger.objects.get()
        self.assertEqual(row.source, "lesson_first_open")
        self.assertEqual(row.amount, expected)
        self.assertEqual(row.idempotency_key, "lesson_first_open:lesson_42")

    def test_total_xp_updates_atomically_across_grants(self):
        a = award_xp(
            self.student, "lesson_first_open", {"lesson_id": 1}, self.grade,
        )
        b = award_xp(
            self.student, "topic_passed", {"topic_id": 99}, self.grade,
        )
        self.assertEqual(self._refresh_profile().total_xp, a + b)

    # ── idempotency ──────────────────────────────────────────────────
    def test_duplicate_grant_returns_zero_and_does_not_double_count(self):
        first = award_xp(
            self.student, "topic_passed", {"topic_id": 7}, self.grade,
        )
        second = award_xp(
            self.student, "topic_passed", {"topic_id": 7}, self.grade,
        )

        self.assertGreater(first, 0)
        self.assertEqual(second, 0)
        self.assertEqual(XPLedger.objects.count(), 1)
        self.assertEqual(self._refresh_profile().total_xp, first)

    def test_distinct_scopes_are_independent_grants(self):
        """Same source, different context keys → both grants land."""
        a = award_xp(
            self.student, "topic_passed", {"topic_id": 1}, self.grade,
        )
        b = award_xp(
            self.student, "topic_passed", {"topic_id": 2}, self.grade,
        )
        self.assertEqual(a, b)
        self.assertEqual(XPLedger.objects.count(), 2)
        self.assertEqual(self._refresh_profile().total_xp, a + b)

    def test_category_tier_cleared_is_one_per_category(self):
        """category_{tier}_tier_cleared keys by category_id, so the same
        tier+category cannot fire twice but different categories can."""
        first = award_xp(
            self.student,
            "category_easy_tier_cleared",
            {"category_id": "addition_compute"},
            self.grade,
        )
        dup = award_xp(
            self.student,
            "category_easy_tier_cleared",
            {"category_id": "addition_compute"},
            self.grade,
        )
        other_cat = award_xp(
            self.student,
            "category_easy_tier_cleared",
            {"category_id": "find_x_addition"},
            self.grade,
        )
        self.assertGreater(first, 0)
        self.assertEqual(dup, 0)
        self.assertEqual(other_cat, first)
        self.assertEqual(self._refresh_profile().total_xp, first + other_cat)

    # ── grade is recorded ────────────────────────────────────────────
    def test_grade_is_recorded_on_ledger_row(self):
        other_grade = Grade.objects.create(number=6, name="Clasa a VI-a")
        award_xp(
            self.student, "lesson_first_open", {"lesson_id": 1}, self.grade,
        )
        award_xp(
            self.student, "lesson_first_open", {"lesson_id": 2}, other_grade,
        )
        rows = XPLedger.objects.order_by("granted_at").all()
        self.assertEqual([r.grade_id for r in rows], [self.grade.id, other_grade.id])

    # ── error and no-op surfaces ─────────────────────────────────────
    def test_unknown_source_raises_keyerror(self):
        with self.assertRaises(KeyError) as cm:
            award_xp(self.student, "no_such_source", {}, self.grade)
        self.assertIn("no_such_source", str(cm.exception))
        self.assertEqual(XPLedger.objects.count(), 0)
        self.assertEqual(self._refresh_profile().total_xp, 0)

    def test_non_student_user_silently_returns_zero(self):
        teacher = User.objects.create_user(
            email="teacher@example.com",
            password="x",
            user_type="teacher",
            first_name="T",
            last_name="T",
        )
        amount = award_xp(
            teacher, "lesson_first_open", {"lesson_id": 1}, self.grade,
        )
        self.assertEqual(amount, 0)
        self.assertFalse(XPLedger.objects.filter(student=teacher).exists())
