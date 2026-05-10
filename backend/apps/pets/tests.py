"""Phase 3 tests: Pet auto-create, atomic pet_xp update, level math."""
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.content.models import Grade
from apps.pets.levels import K, _threshold_for_level, level_for_xp, xp_to_next_level
from apps.pets.models import Pet
from apps.pets.species import GRADE_DEFAULT_SPECIES, default_species_for_grade
from apps.progress.xp import award_xp
from apps.users.models import StudentProfile

User = get_user_model()


class PetAutoCreationTests(TestCase):
    def setUp(self):
        self.grade5 = Grade.objects.create(number=5, name="Clasa a V-a")

    def _make_profile(self, *, grade_number=5, email="alice@example.com"):
        user = User.objects.create_user(
            email=email, password="x", user_type="student",
            first_name="Alice", last_name="A",
        )
        return StudentProfile.objects.create(
            user=user, grade=grade_number, birth_date=date(2014, 1, 1),
        )

    def test_signal_creates_pet_with_default_species(self):
        profile = self._make_profile(grade_number=5)
        pets = list(Pet.objects.filter(student=profile))
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].pet_kind, "pui_de_lup")
        self.assertEqual(pets[0].grade_id, self.grade5.id)
        self.assertEqual(pets[0].pet_xp, 0)

    def test_unmapped_grade_skips_pet_creation(self):
        Grade.objects.create(number=8, name="Clasa a VIII-a")
        profile = self._make_profile(grade_number=8, email="b@example.com")
        self.assertFalse(Pet.objects.filter(student=profile).exists())

    def test_default_species_helper(self):
        self.assertEqual(default_species_for_grade(self.grade5), "pui_de_lup")
        unknown = Grade.objects.create(number=7, name="Clasa a VII-a")
        self.assertIsNone(default_species_for_grade(unknown))
        self.assertIsNone(default_species_for_grade(None))


class PetXPUpdateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grade5 = Grade.objects.create(number=5, name="Clasa a V-a")
        cls.user = User.objects.create_user(
            email="alice@example.com", password="x", user_type="student",
            first_name="Alice", last_name="A",
        )
        cls.profile = StudentProfile.objects.create(
            user=cls.user, grade=5, birth_date=date(2014, 1, 1),
        )

    def test_award_xp_credits_pet_atomically_with_total_xp(self):
        amount = award_xp(
            self.user, "lesson_first_open", {"lesson_id": 1}, self.grade5,
        )
        self.assertGreater(amount, 0)

        self.profile.refresh_from_db()
        pet = Pet.objects.get(student=self.profile, grade=self.grade5)
        self.assertEqual(self.profile.total_xp, amount)
        self.assertEqual(pet.pet_xp, amount)

    def test_award_xp_with_no_matching_pet_only_updates_total_xp(self):
        # Create a Grade 6 row with no default species mapping → no pet.
        grade6 = Grade.objects.create(number=6, name="Clasa a VI-a")
        # Sanity: signal didn't create a pet for grade 6.
        self.assertFalse(
            Pet.objects.filter(student=self.profile, grade=grade6).exists()
        )

        amount = award_xp(
            self.user, "lesson_first_open", {"lesson_id": 99}, grade6,
        )
        self.assertGreater(amount, 0)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_xp, amount)
        # Existing grade-5 pet unchanged.
        pet5 = Pet.objects.get(student=self.profile, grade=self.grade5)
        self.assertEqual(pet5.pet_xp, 0)


class LevelMathTests(TestCase):
    def test_level_floors_at_one(self):
        self.assertEqual(level_for_xp(0), 1)
        self.assertEqual(level_for_xp(-100), 1)

    def test_level_monotonic_non_decreasing(self):
        last = 0
        for xp in range(0, 50_000, 137):
            level = level_for_xp(xp)
            self.assertGreaterEqual(level, last)
            last = level

    def test_known_thresholds(self):
        # Threshold formula: (L-1)^2 * K. K=50 by default.
        # Level 1 starts at 0; level 2 starts at K; level 3 at 4*K.
        self.assertEqual(level_for_xp(0), 1)
        self.assertEqual(level_for_xp(K - 1), 1)
        self.assertEqual(level_for_xp(K), 2)
        self.assertEqual(level_for_xp(4 * K - 1), 2)
        self.assertEqual(level_for_xp(4 * K), 3)

    def test_xp_to_next_level_at_thresholds(self):
        # Just-promoted to level 2: gap to level 3 is 4K - K = 3K.
        self.assertEqual(xp_to_next_level(K), 3 * K)
        # At xp=0 (level 1): gap to level 2 is K.
        self.assertEqual(xp_to_next_level(0), K)
        # Mid-level: at xp=K+10, level=2, next threshold=4K, gap=3K-10.
        self.assertEqual(xp_to_next_level(K + 10), 3 * K - 10)

    def test_threshold_helper_matches_level_inverse(self):
        # _threshold_for_level(L) is the smallest XP that produces level L.
        for level in [1, 2, 3, 5, 10, 50]:
            t = _threshold_for_level(level)
            self.assertEqual(level_for_xp(t), level)
            if level > 1:
                self.assertEqual(level_for_xp(t - 1), level - 1)


class SpeciesRegistryTests(TestCase):
    def test_grade_5_maps_to_pui_de_lup(self):
        self.assertEqual(GRADE_DEFAULT_SPECIES[5], "pui_de_lup")
