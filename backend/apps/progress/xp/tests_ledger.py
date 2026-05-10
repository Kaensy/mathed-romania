"""Phase 4 API tests: XP ledger endpoint."""
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.content.models import Grade
from apps.progress.xp import XPLedger
from apps.progress.xp.awards import XP_AWARDS
from apps.users.models import StudentProfile

User = get_user_model()


def _make_student(*, grade_number=5, email="alice@example.com"):
    user = User.objects.create_user(
        email=email, password="x", user_type="student",
        first_name="Alice", last_name="A",
    )
    StudentProfile.objects.create(
        user=user, grade=grade_number, birth_date=date(2014, 1, 1),
    )
    return user


def _make_teacher():
    return User.objects.create_user(
        email="t@example.com", password="x", user_type="teacher",
        first_name="T", last_name="T",
    )


def _seed_ledger_row(user, *, source="lesson_first_open", grade, key_suffix, amount=5, when=None):
    row = XPLedger.objects.create(
        student=user,
        source=source,
        amount=amount,
        grade=grade,
        idempotency_key=f"{source}:{key_suffix}",
    )
    if when is not None:
        XPLedger.objects.filter(pk=row.pk).update(granted_at=when)
    return row


class XPLedgerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grade5 = Grade.objects.create(number=5, name="Clasa a V-a")
        cls.grade6 = Grade.objects.create(number=6, name="Clasa a VI-a")
        cls.user = _make_student()

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_403_for_non_student(self):
        teacher = _make_teacher()
        client = APIClient()
        client.force_authenticate(teacher)
        resp = client.get(reverse("xp_ledger"))
        self.assertEqual(resp.status_code, 403)

    def test_returns_rows_newest_first(self):
        now = timezone.now()
        _seed_ledger_row(self.user, grade=self.grade5, key_suffix="a", when=now - timedelta(hours=2))
        _seed_ledger_row(self.user, grade=self.grade5, key_suffix="b", when=now - timedelta(hours=1))
        _seed_ledger_row(self.user, grade=self.grade5, key_suffix="c", when=now)

        resp = self.client.get(reverse("xp_ledger"))
        self.assertEqual(resp.status_code, 200)
        rows = resp.data["results"]
        timestamps = [r["granted_at"] for r in rows]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))

    def test_source_display_resolves_against_registry(self):
        _seed_ledger_row(
            self.user, grade=self.grade5,
            source="topic_passed", key_suffix="topic_1",
        )
        resp = self.client.get(reverse("xp_ledger"))
        row = resp.data["results"][0]
        self.assertEqual(row["source"], "topic_passed")
        self.assertEqual(
            row["source_display"], XP_AWARDS["topic_passed"]["display_name"],
        )

    def test_unknown_source_falls_back_to_slug(self):
        _seed_ledger_row(
            self.user, grade=self.grade5,
            source="legacy_source", key_suffix="x",
        )
        resp = self.client.get(reverse("xp_ledger"))
        row = resp.data["results"][0]
        self.assertEqual(row["source_display"], "legacy_source")

    def test_grade_filter_scopes_to_one_grade(self):
        _seed_ledger_row(self.user, grade=self.grade5, key_suffix="g5a")
        _seed_ledger_row(self.user, grade=self.grade5, key_suffix="g5b")
        _seed_ledger_row(self.user, grade=self.grade6, key_suffix="g6a")

        resp = self.client.get(reverse("xp_ledger"), {"grade": 5})
        self.assertEqual(resp.status_code, 200)
        grade_numbers = {r["grade_number"] for r in resp.data["results"]}
        self.assertEqual(grade_numbers, {5})
        self.assertEqual(resp.data["count"], 2)

    def test_invalid_grade_param_400(self):
        resp = self.client.get(reverse("xp_ledger"), {"grade": "abc"})
        self.assertEqual(resp.status_code, 400)

    def test_pagination_caps_at_50_per_page(self):
        # 60 rows: page 1 → 50 results, page 2 → 10 results.
        for i in range(60):
            _seed_ledger_row(self.user, grade=self.grade5, key_suffix=str(i))

        page1 = self.client.get(reverse("xp_ledger"))
        self.assertEqual(len(page1.data["results"]), 50)
        self.assertEqual(page1.data["count"], 60)
        self.assertIsNotNone(page1.data["next"])

        page2 = self.client.get(reverse("xp_ledger"), {"page": 2})
        self.assertEqual(len(page2.data["results"]), 10)
        self.assertIsNone(page2.data["next"])

    def test_each_row_has_expected_fields(self):
        _seed_ledger_row(
            self.user, grade=self.grade5,
            source="daily_test_complete", key_suffix="x", amount=30,
        )
        resp = self.client.get(reverse("xp_ledger"))
        row = resp.data["results"][0]
        self.assertEqual(
            set(row.keys()),
            {"source", "source_display", "amount", "granted_at", "grade_number"},
        )
        self.assertEqual(row["amount"], 30)
        self.assertEqual(row["grade_number"], 5)
