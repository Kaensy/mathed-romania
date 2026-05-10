"""Phase 6 tests: pet_level_up + xp_milestone badge events fired from
inside award_xp's transaction."""
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.content.models import Grade
from apps.pets.levels import K, _threshold_for_level
from apps.pets.models import Pet
from apps.progress.models import Achievement
from apps.progress.xp import award_xp
from apps.users.models import StudentProfile

User = get_user_model()


def _make_student():
    user = User.objects.create_user(
        email="alice@example.com", password="x", user_type="student",
        first_name="Alice", last_name="A",
    )
    StudentProfile.objects.create(
        user=user, grade=5, birth_date=date(2014, 1, 1),
    )
    return user


def _set_pet_xp(user, grade, xp: int) -> Pet:
    """Force-set the pet's xp without going through award_xp (used to
    seed the test into a specific level/total state)."""
    pet = Pet.objects.get(student__user=user, grade=grade)
    pet.pet_xp = xp
    pet.save(update_fields=["pet_xp"])
    return pet


def _set_total_xp(user, xp: int):
    StudentProfile.objects.filter(user=user).update(total_xp=xp)


class PetLevelUpEventTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grade5 = Grade.objects.create(number=5, name="Clasa a V-a")
        cls.user = _make_student()

    def _award(self, source="lesson_first_open", lesson_id=1):
        # Each lesson_id keeps idempotency keys distinct so subsequent
        # calls actually grant XP rather than no-op.
        return award_xp(
            self.user, source, {"lesson_id": lesson_id}, self.grade5,
        )

    def test_no_event_when_grant_does_not_cross_a_level(self):
        # Seed at level 1 (xp = 10), grant a small lesson_first_open (5
        # XP). New xp = 15, still level 1.
        _set_pet_xp(self.user, self.grade5, 10)
        self._award(lesson_id=1)
        self.assertFalse(
            Achievement.objects.filter(
                student=self.user, badge_key__startswith="pet_level_",
            ).exists()
        )

    def test_crossing_level_10_awards_pet_level_10(self):
        # Threshold for level 10 = 9^2 * K. Seed one XP under threshold
        # for level 10, then grant enough to cross it.
        target = _threshold_for_level(10)
        _set_pet_xp(self.user, self.grade5, target - 1)
        # `unit_passed` grants 200 XP, easily crossing the threshold.
        award_xp(
            self.user, "unit_passed", {"unit_id": 1}, self.grade5,
        )
        self.assertTrue(
            Achievement.objects.filter(
                student=self.user, badge_key="pet_level_10",
            ).exists()
        )

    def test_crossing_level_25_awards_both_level_10_and_25(self):
        target = _threshold_for_level(25)
        _set_pet_xp(self.user, self.grade5, target - 1)
        award_xp(
            self.user, "unit_passed", {"unit_id": 1}, self.grade5,
        )
        keys = set(
            Achievement.objects.filter(student=self.user).values_list(
                "badge_key", flat=True,
            )
        )
        # Multi-level evaluators all qualify when new_level >= 25.
        self.assertIn("pet_level_10", keys)
        self.assertIn("pet_level_25", keys)

    def test_milestone_badges_idempotent_on_subsequent_grants(self):
        target = _threshold_for_level(10)
        _set_pet_xp(self.user, self.grade5, target - 1)
        award_xp(
            self.user, "unit_passed", {"unit_id": 1}, self.grade5,
        )
        award_xp(
            self.user, "topic_passed", {"topic_id": 1}, self.grade5,
        )
        # No duplicate Achievement rows.
        self.assertEqual(
            Achievement.objects.filter(
                student=self.user, badge_key="pet_level_10",
            ).count(),
            1,
        )

    def test_no_event_when_pet_does_not_exist_for_grade(self):
        # Grade 6 has no default pet species.
        grade6 = Grade.objects.create(number=6, name="Clasa a VI-a")
        award_xp(
            self.user, "lesson_first_open", {"lesson_id": 99}, grade6,
        )
        self.assertFalse(
            Achievement.objects.filter(
                student=self.user, badge_key__startswith="pet_level_",
            ).exists()
        )


class XPMilestoneEventTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grade5 = Grade.objects.create(number=5, name="Clasa a V-a")
        cls.user = _make_student()

    def test_below_threshold_no_milestone(self):
        _set_total_xp(self.user, 500)
        award_xp(
            self.user, "lesson_first_open", {"lesson_id": 1}, self.grade5,
        )
        self.assertFalse(
            Achievement.objects.filter(
                student=self.user, badge_key="xp_milestone_1k",
            ).exists()
        )

    def test_just_under_threshold_no_milestone(self):
        _set_total_xp(self.user, 994)
        # lesson_first_open grants 5 XP → 999, still under 1000.
        award_xp(
            self.user, "lesson_first_open", {"lesson_id": 1}, self.grade5,
        )
        self.assertFalse(
            Achievement.objects.filter(
                student=self.user, badge_key="xp_milestone_1k",
            ).exists()
        )

    def test_crossing_thousand_boundary_awards_milestone_1k(self):
        _set_total_xp(self.user, 999)
        award_xp(
            self.user, "lesson_first_open", {"lesson_id": 1}, self.grade5,
        )
        self.assertTrue(
            Achievement.objects.filter(
                student=self.user, badge_key="xp_milestone_1k",
            ).exists()
        )

    def test_landing_exactly_on_thousand_awards_milestone_1k(self):
        _set_total_xp(self.user, 995)
        # +5 XP lands exactly at 1000.
        award_xp(
            self.user, "lesson_first_open", {"lesson_id": 1}, self.grade5,
        )
        self.assertTrue(
            Achievement.objects.filter(
                student=self.user, badge_key="xp_milestone_1k",
            ).exists()
        )

    def test_crossing_ten_thousand_awards_both_1k_and_10k(self):
        _set_total_xp(self.user, 9995)
        award_xp(
            self.user, "lesson_first_open", {"lesson_id": 1}, self.grade5,
        )
        keys = set(
            Achievement.objects.filter(student=self.user).values_list(
                "badge_key", flat=True,
            )
        )
        self.assertIn("xp_milestone_1k", keys)
        self.assertIn("xp_milestone_10k", keys)

    def test_repeated_crossings_idempotent(self):
        _set_total_xp(self.user, 999)
        award_xp(
            self.user, "lesson_first_open", {"lesson_id": 1}, self.grade5,
        )
        # Second grant lands at 1010 — still in the same 1k bucket as
        # the previous, so no new milestone fires.
        award_xp(
            self.user, "lesson_first_open", {"lesson_id": 2}, self.grade5,
        )
        self.assertEqual(
            Achievement.objects.filter(
                student=self.user, badge_key="xp_milestone_1k",
            ).count(),
            1,
        )

    def test_unused_constant_K_proves_threshold_helper_is_imported_for_pet_tests(self):
        # Smoke check that K is importable; pet-level tests use
        # _threshold_for_level which depends on K.
        self.assertGreater(K, 0)
