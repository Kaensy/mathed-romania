"""One-time cosmetic backfill.

Provisions every existing student exactly as a fresh sign-up now is:
runs the full unlock evaluator (so each student already owns every
cosmetic their current XP / badges / claimed quests satisfy) and
default-equips the plainest starter frame + the parchment theme.

This deliberately calls the live `provision_student_cosmetics` service
rather than re-deriving the rules against historical models — the
catalog and evaluator are the single source of truth, and this is the
tip migration with the current schema. The work is idempotent
(get_or_create throughout), so a re-run grants and equips nothing new;
a single problem student is logged and skipped rather than aborting the
whole backfill. Reverse is a no-op — we never strip cosmetics on
downgrade.
"""
import logging

from django.db import migrations

logger = logging.getLogger(__name__)


def backfill_cosmetics(apps, schema_editor):
    # Real model + service on purpose (see module docstring): the
    # evaluator must run "fully". Imported here, not at module top, so
    # migration loading stays cheap and import-safe.
    from apps.progress.cosmetics.service import provision_student_cosmetics
    from apps.users.models import StudentProfile

    qs = StudentProfile.objects.select_related("user").iterator()
    granted = failed = students = 0
    for profile in qs:
        students += 1
        try:
            newly = provision_student_cosmetics(profile.user)
            granted += len(newly)
        except Exception:
            failed += 1
            logger.warning(
                "Cosmetic backfill failed for student profile #%s",
                profile.pk,
                exc_info=True,
            )
    logger.info(
        "Cosmetic backfill: %s students, %s cosmetics newly granted, "
        "%s failures",
        students,
        granted,
        failed,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("progress", "0016_cosmetics_foundation"),
        ("users", "0003_studentprofile_avatar"),
    ]

    operations = [
        migrations.RunPython(backfill_cosmetics, migrations.RunPython.noop),
    ]
