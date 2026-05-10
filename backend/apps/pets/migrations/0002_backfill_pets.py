"""Backfill Pets for StudentProfiles that existed before Phase 3.

The post_save signal only fires on newly-saved profiles, so any profile
already in the DB needs an explicit pass. Uses the same
default_species_for_grade map as the signal — students whose grade has
no entry are skipped (no pet created), matching live behavior."""
from django.db import migrations


def backfill_pets(apps, schema_editor):
    StudentProfile = apps.get_model("users", "StudentProfile")
    Grade = apps.get_model("content", "Grade")
    Pet = apps.get_model("pets", "Pet")

    # Inline the species map so the migration is self-contained and
    # immune to future edits of apps.pets.species.
    GRADE_DEFAULT_SPECIES = {5: "pui_de_lup"}

    grade_by_number = {g.number: g for g in Grade.objects.all()}

    for profile in StudentProfile.objects.all():
        kind = GRADE_DEFAULT_SPECIES.get(profile.grade)
        if kind is None:
            continue
        grade = grade_by_number.get(profile.grade)
        if grade is None:
            continue
        Pet.objects.get_or_create(
            student=profile,
            grade=grade,
            defaults={"pet_kind": kind},
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("pets", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(backfill_pets, reverse_code=noop),
    ]
