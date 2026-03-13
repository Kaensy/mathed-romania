"""
Replace Lesson.content (TextField) with Lesson.blocks (JSONField).

Safe to run: all lesson content is placeholder/unpublished at this stage.
The old content field is dropped; blocks defaults to an empty list.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        # Update this to match your last migration file name exactly.
        # Run: python manage.py showmigrations content
        # and replace the string below with your actual latest migration.
        ("content", "0002_lesson_summary_glossaryterm"),
    ]

    operations = [
        # Remove old TextField
        migrations.RemoveField(
            model_name="lesson",
            name="content",
        ),
        # Add new JSONField
        migrations.AddField(
            model_name="lesson",
            name="blocks",
            field=models.JSONField(
                default=list,
                help_text=(
                    "Structured lesson content as an array of typed blocks. "
                    "See BLOCK_SCHEMA.md for the full specification."
                ),
            ),
        ),
        # Add drag_order and click_select exercise types
        # (these are CharField choices — no migration needed for choices,
        # but documenting the intent here)
    ]
