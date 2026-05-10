"""Auto-create a Pet when a StudentProfile is first saved.

Skips silently when the student's grade has no default species — the
backfill data migration uses the same skip-if-unmapped rule, so the two
paths stay consistent.
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.content.models import Grade
from apps.users.models import StudentProfile

from .models import Pet
from .species import default_species_for_grade

logger = logging.getLogger(__name__)


@receiver(post_save, sender=StudentProfile)
def create_default_pet(sender, instance, created, **kwargs):
    if not created:
        return

    grade = Grade.objects.filter(number=instance.grade).first()
    kind = default_species_for_grade(grade)
    if kind is None:
        return

    try:
        Pet.objects.get_or_create(
            student=instance,
            grade=grade,
            defaults={"pet_kind": kind},
        )
    except Exception:
        logger.warning("Pet auto-create failed", exc_info=True)
