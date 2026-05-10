"""Pet model — one per (student, grade)."""
from django.db import models

from .species import species_choices


class Pet(models.Model):
    student = models.ForeignKey(
        "users.StudentProfile",
        on_delete=models.CASCADE,
        related_name="pets",
    )
    grade = models.ForeignKey(
        "content.Grade",
        on_delete=models.PROTECT,
        related_name="pets",
    )
    pet_kind = models.CharField(
        max_length=50,
        choices=species_choices(),
        help_text="Slug from apps.pets.species.PET_SPECIES.",
    )
    pet_xp = models.PositiveIntegerField(default=0, db_index=True)
    name = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Optional custom name. Empty falls back to species default_name.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pets"
        unique_together = [("student", "grade")]
        ordering = ["-created_at"]

    def __str__(self):
        label = self.name or self.pet_kind
        return f"{label} (student #{self.student_id}, grade {self.grade_id})"
