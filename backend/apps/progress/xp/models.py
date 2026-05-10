"""XP ledger model.

Append-only log of every XP grant. The (student, idempotency_key)
unique constraint is the one-grant-per-event guarantee — duplicate
inserts hit IntegrityError and are caught by `award_xp`.
"""
from django.conf import settings
from django.db import models


class XPLedger(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="xp_grants",
        limit_choices_to={"user_type": "student"},
    )
    source = models.CharField(
        max_length=64,
        db_index=True,
        help_text="Slug from XP_AWARDS (e.g. 'topic_passed').",
    )
    amount = models.IntegerField()
    grade = models.ForeignKey(
        "content.Grade",
        on_delete=models.PROTECT,
        related_name="xp_grants",
        help_text="Grade context the grant was earned in. Drives per-grade leaderboards.",
    )
    idempotency_key = models.CharField(max_length=128, db_index=True)
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "progress"
        db_table = "xp_ledger"
        unique_together = [("student", "idempotency_key")]
        ordering = ["-granted_at"]

    def __str__(self):
        return f"{self.student.email} +{self.amount} ({self.source})"
