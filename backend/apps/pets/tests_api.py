"""Phase 4 API tests: pet GET/PATCH endpoints."""
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.content.models import Grade
from apps.pets.levels import K, level_for_xp, xp_to_next_level
from apps.pets.models import Pet
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


def _make_teacher(email="teach@example.com"):
    return User.objects.create_user(
        email=email, password="x", user_type="teacher",
        first_name="T", last_name="T",
    )


class PetGetMeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grade5 = Grade.objects.create(number=5, name="Clasa a V-a")
        cls.user = _make_student()
        cls.profile = cls.user.student_profile
        cls.pet = Pet.objects.get(student=cls.profile, grade=cls.grade5)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_get_returns_computed_fields(self):
        # Bump pet_xp to land mid-level so xp_to_next_level is non-trivial.
        self.pet.pet_xp = K + 10
        self.pet.save(update_fields=["pet_xp"])
        self.profile.total_xp = K + 10
        self.profile.save(update_fields=["total_xp"])

        resp = self.client.get(reverse("pet_me"))
        self.assertEqual(resp.status_code, 200)
        data = resp.data
        self.assertEqual(data["pet_kind"], "pui_de_lup")
        self.assertEqual(data["kind_display"], "Pui de lup")
        self.assertEqual(data["pet_xp"], K + 10)
        self.assertEqual(data["level"], level_for_xp(K + 10))
        self.assertEqual(data["xp_to_next_level"], xp_to_next_level(K + 10))
        self.assertEqual(data["grade_number"], 5)
        self.assertEqual(data["total_xp"], K + 10)

    def test_display_name_falls_back_to_default_when_blank(self):
        self.pet.name = ""
        self.pet.save(update_fields=["name"])
        resp = self.client.get(reverse("pet_me"))
        self.assertEqual(resp.data["display_name"], "Lupul")

    def test_display_name_uses_custom_when_set(self):
        self.pet.name = "Maraș"
        self.pet.save(update_fields=["name"])
        resp = self.client.get(reverse("pet_me"))
        self.assertEqual(resp.data["display_name"], "Maraș")

    def test_404_when_no_pet_for_current_grade(self):
        # Move student to a grade with no default species.
        Grade.objects.create(number=8, name="Clasa a VIII-a")
        self.profile.grade = 8
        self.profile.save(update_fields=["grade"])
        resp = self.client.get(reverse("pet_me"))
        self.assertEqual(resp.status_code, 404)

    def test_403_for_non_student(self):
        teacher = _make_teacher()
        client = APIClient()
        client.force_authenticate(teacher)
        resp = client.get(reverse("pet_me"))
        self.assertEqual(resp.status_code, 403)


class PetPatchMeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grade5 = Grade.objects.create(number=5, name="Clasa a V-a")
        cls.user = _make_student()
        cls.profile = cls.user.student_profile
        cls.pet = Pet.objects.get(student=cls.profile, grade=cls.grade5)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def _patch(self, name):
        return self.client.patch(reverse("pet_me"), {"name": name}, format="json")

    def test_accepts_unicode_with_diacritics(self):
        resp = self._patch("Lupul Maraș")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.name, "Lupul Maraș")
        self.assertEqual(resp.data["display_name"], "Lupul Maraș")

    def test_accepts_hyphenated_name(self):
        resp = self._patch("Făt-Frumos")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.name, "Făt-Frumos")

    def test_strips_leading_and_trailing_whitespace(self):
        resp = self._patch("  Maraș  ")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.name, "Maraș")

    def test_blank_clears_name(self):
        self.pet.name = "Existing"
        self.pet.save(update_fields=["name"])
        resp = self._patch("   ")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.name, "")
        self.assertEqual(resp.data["display_name"], "Lupul")

    def test_rejects_too_long(self):
        resp = self._patch("X" * 31)
        self.assertEqual(resp.status_code, 400)

    def test_rejects_emoji(self):
        resp = self._patch("Maraș🐺")
        self.assertEqual(resp.status_code, 400)

    def test_rejects_digits(self):
        resp = self._patch("Lupul1")
        self.assertEqual(resp.status_code, 400)

    def test_rejects_special_chars(self):
        resp = self._patch("Lupul!")
        self.assertEqual(resp.status_code, 400)

    def test_403_for_non_student(self):
        teacher = _make_teacher()
        client = APIClient()
        client.force_authenticate(teacher)
        resp = client.patch(reverse("pet_me"), {"name": "X"}, format="json")
        self.assertEqual(resp.status_code, 403)
