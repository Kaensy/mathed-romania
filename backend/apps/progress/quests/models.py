"""Quest state models.

Two per-student tables, both registered with the `progress` app (the
package mirrors `xp/` and `badges/`; like `XPLedger` they set
`app_label = "progress"` explicitly and are re-exported into
`apps/progress/models.py` so Django discovers them).

- QuestAssignment: one row per (student, quest, period) — the live
  instance of a catalog quest for a given day/week.
- DailyChallengeProgress: one row per (student, day) — the daily
  points bar that the milestone rungs are claimed against.

`quest_slug` is a free-form CharField (same migration-free contract as
`XPLedger.source` / `Achievement.badge_key`): editing the catalog never
needs a migration, and `target` is snapshotted at row creation so a
later catalog tweak can't move the goalposts on an in-flight quest.

Models + config only this phase — no assignment/claim logic here.
"""
from django.db import models


class QuestAssignment(models.Model):
    """A catalog quest materialised for one student in one period.

    `period_key` is the Europe/Bucharest period this assignment belongs
    to (see apps.progress.quests.periods): the ISO date for daily
    quests ("2026-05-18") or the ISO year+week for weekly quests
    ("2026-W21"). The (student, quest_slug, period_key) uniqueness is
    what makes "one daily login quest per day" a database guarantee.
    """

    class Cadence(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CLAIMED = "claimed", "Claimed"
        EXPIRED = "expired", "Expired"

    student = models.ForeignKey(
        "users.StudentProfile",
        on_delete=models.CASCADE,
        related_name="quest_assignments",
    )
    quest_slug = models.CharField(
        max_length=64,
        help_text="Slug from QUEST_CATALOG. Free-form: catalog edits need no migration.",
    )
    cadence = models.CharField(max_length=8, choices=Cadence.choices)
    period_key = models.CharField(
        max_length=16,
        help_text="Bucharest-local ISO date (daily) or ISO year+week (weekly).",
    )
    progress = models.PositiveIntegerField(default=0)
    target = models.PositiveIntegerField(
        help_text="target_count snapshotted from the catalog at creation.",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    claimed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "progress"
        db_table = "quest_assignments"
        unique_together = [("student", "quest_slug", "period_key")]
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"student #{self.student_id} — {self.quest_slug} "
            f"[{self.period_key}] {self.progress}/{self.target} ({self.status})"
        )


class DailyChallengeProgress(models.Model):
    """The daily points bar for one student on one Bucharest-local day.

    `points` accumulates DEFAULT_DAILY_POINTS per claimed daily quest;
    `claimed_thresholds` records which DAILY_MILESTONES rungs have been
    cashed in. It is treated as an unordered set of threshold ints — no
    consumer may assume the list is sorted or contiguous.
    """

    student = models.ForeignKey(
        "users.StudentProfile",
        on_delete=models.CASCADE,
        related_name="daily_challenge_progress",
    )
    date = models.DateField(help_text="Europe/Bucharest local date.")
    points = models.PositiveIntegerField(default=0)
    claimed_thresholds = models.JSONField(
        default=list,
        help_text="Claimed DAILY_MILESTONES thresholds, e.g. [20, 60]. Unordered set.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "progress"
        db_table = "daily_challenge_progress"
        unique_together = [("student", "date")]
        ordering = ["-date"]

    def __str__(self):
        return (
            f"student #{self.student_id} — {self.date} "
            f"{self.points}p (claimed {self.claimed_thresholds})"
        )
