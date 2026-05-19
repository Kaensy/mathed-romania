"""Cosmetic ownership state.

One per-student table, registered with the `progress` app. Like
`XPLedger` and the quest models it sets `app_label = "progress"`
explicitly and is re-exported into `apps/progress/models.py` so Django
discovers it.

- StudentCosmetic: one row per (student, cosmetic) the student has
  unlocked — when it was unlocked, and whether it is currently equipped.

`cosmetic_slug` is a free-form CharField (same migration-free contract
as `XPLedger.source` / `QuestAssignment.quest_slug`): editing
COSMETIC_CATALOG never needs a migration. `cosmetic_type` is snapshotted
from the catalog at row creation so the "one equipped per type"
constraint can be enforced at the database level without a catalog
lookup (and so an in-flight row keeps its type even if the catalog is
later edited).

Model + constraints only this phase — no unlock evaluator, no equip
endpoint, no signals.
"""
from django.db import models


class StudentCosmetic(models.Model):
    """A catalog cosmetic a student has unlocked.

    The two constraints encode the invariants:

    - ``uniq_student_cosmetic`` — a student owns a given cosmetic at
      most once (no duplicate ownership rows).
    - ``uniq_one_equipped_per_type`` — a partial unique index over
      (student, cosmetic_type) restricted to equipped rows: at most one
      equipped cosmetic per type per student. "Exactly one" (a starter
      always equipped) is a service-layer guarantee for a later phase;
      the database here only forbids two-equipped.
    """

    class CosmeticType(models.TextChoices):
        FRAME = "frame", "Frame"
        PROFILE_THEME = "profile_theme", "Profile Theme"
        AVATAR = "avatar", "Avatar"

    student = models.ForeignKey(
        "users.StudentProfile",
        on_delete=models.CASCADE,
        related_name="cosmetics",
    )
    cosmetic_slug = models.CharField(
        max_length=64,
        help_text="Slug from COSMETIC_CATALOG. Free-form: catalog edits need no migration.",
    )
    cosmetic_type = models.CharField(
        max_length=16,
        choices=CosmeticType.choices,
        help_text="type snapshotted from the catalog at creation; drives the one-equipped-per-type constraint.",
    )
    is_equipped = models.BooleanField(default=False)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "progress"
        db_table = "student_cosmetics"
        ordering = ["-unlocked_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "cosmetic_slug"],
                name="uniq_student_cosmetic",
            ),
            models.UniqueConstraint(
                fields=["student", "cosmetic_type"],
                condition=models.Q(is_equipped=True),
                name="uniq_one_equipped_per_type",
            ),
        ]

    def __str__(self):
        equipped = " [equipped]" if self.is_equipped else ""
        return f"student #{self.student_id} — {self.cosmetic_slug}{equipped}"
