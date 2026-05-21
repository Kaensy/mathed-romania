"""
seed_test_progress — reset one named student and re-apply a representative
progress state so the wardrobe modal has a real mix to review.

Idempotent: runs cleanly on a fresh student, and a re-run wipes whatever
state the previous run produced before re-applying the same end state.

What it applies:
- total_xp pushed to a value that crosses *most* (not all) frame and
  avatar XP thresholds, leaving frame_ornate / avatar_ranger-class entries
  beyond reach as locked entries to review.
- A curated set of achievements drawn from all four badge families, each
  gating a cosmetic across all three cosmetic types.
- One claimed weekly quest that gates a cosmetic.

After the state is in place we call `safe_provision_student_cosmetics`,
which is the same call student-profile creation makes. That funnels every
seeded condition through the live unlock evaluator — cosmetics arrive
*organically* rather than being directly inserted, so we never drift away
from what a real student would experience.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.progress.cosmetics.service import safe_provision_student_cosmetics
from apps.progress.models import (
    Achievement,
    DailyTestSession,
    Streak,
    StreakActivity,
)
from apps.progress.quests.models import DailyChallengeProgress, QuestAssignment
from apps.progress.quests.periods import today_local, weekly_period_key
from apps.progress.xp.models import XPLedger
from apps.users.models import StudentProfile, User

# Tunables. Picked so the post-seed catalog has a real owned/locked mix
# across all three unlock kinds.

# Crosses iron(250), bronze(1000), silver(2500), gold(5000) frames and
# squire(500), ranger(3000) avatars. Leaves ornate(10000) locked.
SEEDED_TOTAL_XP = 6500

# One badge per family, each gating a cosmetic of a different type:
#   unit_1_complete      → progress     → frame_laurel
#   topic_perfect        → mastery      → frame_crown
#   streak_7             → consistency  → avatar_steady_learner
#   unit_fully_explored  → discovery    → theme_old_library
# Leaves the rest of the cosmetic-gating badges (hard_tier_x5, streak_30,
# pet_level_25/50, xp_milestone_10k, test_perfect_score) unawarded, so
# their cosmetics remain visibly locked in the wardrobe.
SEEDED_BADGE_KEYS = [
    "unit_1_complete",
    "topic_perfect",
    "streak_7",
    "unit_fully_explored",
]

# One claimed weekly quest. Gates the frame_quest_hunter cosmetic. Leaves
# weekly_exercise and weekly_test_passed unclaimed, so frame_whetstone
# and avatar_test_collector stay locked.
SEEDED_QUEST_SLUG = "weekly_quests_claimed"


class Command(BaseCommand):
    help = (
        "Reset a named student and re-seed a representative progress state "
        "so the cosmetic wardrobe has a realistic mix to review."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            help=(
                "Student's email (USERNAME_FIELD on the User model). "
                "Must already exist; this command never creates accounts."
            ),
        )

    def handle(self, *args, **options):
        email = options["username"]

        user = User.objects.filter(email=email).first()
        if user is None:
            raise CommandError(f"No user with email {email!r}.")
        if not user.is_student:
            raise CommandError(
                f"User {email!r} is not a student (user_type={user.user_type!r})."
            )
        profile = StudentProfile.objects.filter(user=user).first()
        if profile is None:
            raise CommandError(
                f"User {email!r} has no StudentProfile — registration is incomplete."
            )

        self.stdout.write(f"Seeding test progress for {email} (#{user.pk})…")

        with transaction.atomic():
            self._reset_student(user, profile)
            self._apply_state(user, profile)

        # safe_provision_student_cosmetics runs outside the wipe/apply
        # block so its side effects (logging, etc.) are committed on the
        # state we just persisted, not held inside the same transaction.
        safe_provision_student_cosmetics(user)

        self._report(user, profile)

    # ── Reset ───────────────────────────────────────────────────────────────

    def _reset_student(self, user, profile):
        """Wipe everything the unlock evaluator consults plus the avatar
        upload, so the apply step starts from a clean baseline. Identity
        (User, StudentProfile) is preserved; lesson/exercise/test progress
        is left alone — those don't feed the cosmetic system."""
        # Cosmetic rows themselves — `provision_student_cosmetics` will
        # re-create starters and re-equip defaults.
        profile.cosmetics.all().delete()

        Achievement.objects.filter(student=user).delete()
        XPLedger.objects.filter(student=user).delete()

        QuestAssignment.objects.filter(student=profile).delete()
        DailyChallengeProgress.objects.filter(student=profile).delete()

        # Streak — including activity rows so a re-run can't be tricked
        # into thinking today was already active.
        StreakActivity.objects.filter(student=user).delete()
        Streak.objects.filter(student=user).delete()

        # Daily test sessions hold no cosmetic state but accumulate
        # date-keyed rows on re-runs; clear them so the dashboard surfaces
        # remain consistent.
        DailyTestSession.objects.filter(student=user).delete()

        # Reset profile counters and avatar storage. Delete the uploaded
        # file from MEDIA_ROOT/avatars/ if present so a re-run never
        # leaves orphans.
        profile.total_xp = 0
        profile.avatar_source = StudentProfile.AvatarSource.MONOGRAM
        if profile.avatar_image:
            try:
                profile.avatar_image.delete(save=False)
            except Exception:
                # Storage hiccup shouldn't block the reset; the seed is
                # for dev use and the orphan can be cleaned manually.
                self.stdout.write(
                    self.style.WARNING(
                        "  (failed to delete previous avatar file — orphan possible)"
                    )
                )
        profile.save(
            update_fields=["total_xp", "avatar_source", "avatar_image"]
        )

    # ── Apply ───────────────────────────────────────────────────────────────

    def _apply_state(self, user, profile):
        """Apply the seeded XP, achievements, and claimed quest. The
        cosmetic unlocks happen in the follow-on
        safe_provision_student_cosmetics call — this only sets up the
        conditions the evaluator reads."""
        profile.total_xp = SEEDED_TOTAL_XP
        profile.save(update_fields=["total_xp"])

        for badge_key in SEEDED_BADGE_KEYS:
            Achievement.objects.get_or_create(
                student=user, badge_key=badge_key,
            )

        # Park the claimed quest in the current weekly period so it shows
        # up consistently on the quests page if anyone looks. Its target
        # is snapshotted from the catalog as the model expects.
        from apps.progress.quests.catalog import QUEST_CATALOG

        quest = QUEST_CATALOG[SEEDED_QUEST_SLUG]
        today = today_local()
        QuestAssignment.objects.update_or_create(
            student=profile,
            quest_slug=SEEDED_QUEST_SLUG,
            period_key=weekly_period_key(today),
            defaults={
                "cadence": QuestAssignment.Cadence.WEEKLY,
                "target": quest.target_count,
                "progress": quest.target_count,
                "status": QuestAssignment.Status.CLAIMED,
            },
        )

    # ── Report ──────────────────────────────────────────────────────────────

    def _report(self, user, profile):
        """One-shot summary so the operator can see what the seed produced
        without having to query the DB."""
        profile.refresh_from_db()
        owned = profile.cosmetics.count()
        equipped = profile.cosmetics.filter(is_equipped=True).count()
        from apps.progress.cosmetics.catalog import COSMETIC_CATALOG

        total = len(COSMETIC_CATALOG)
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Seeded state:"))
        self.stdout.write(f"  total_xp:           {profile.total_xp}")
        self.stdout.write(
            f"  achievements:       {Achievement.objects.filter(student=user).count()} "
            f"({', '.join(SEEDED_BADGE_KEYS)})"
        )
        self.stdout.write(
            f"  claimed quests:     1 ({SEEDED_QUEST_SLUG})"
        )
        self.stdout.write(
            f"  cosmetics owned:    {owned} / {total} "
            f"({total - owned} still locked)"
        )
        self.stdout.write(f"  cosmetics equipped: {equipped}")
        self.stdout.write(f"  avatar_source:      {profile.avatar_source}")
