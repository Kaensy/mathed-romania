"""
Adds:
  - ExerciseAttempt.session_id  (UUIDField, nullable, indexed)
  - CategoryProgress model

Check the dependency below — it must match the last migration in the
progress app in your project (visible via `python manage.py showmigrations progress`).
"""
import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    # !! VERIFY THIS: replace '0002_initial' with the actual last migration
    # in your progress app if it differs.
    dependencies = [
        ("progress", "0002_initial"),
        ("content", "0006_test_scope_category"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── 1. Add session_id to ExerciseAttempt ──────────────────────────
        migrations.AddField(
            model_name="exerciseattempt",
            name="session_id",
            field=models.UUIDField(
                blank=True,
                db_index=True,
                help_text="Groups attempts from a single practice batch",
                null=True,
            ),
        ),

        # ── 2. Create CategoryProgress ────────────────────────────────────
        migrations.CreateModel(
            name="CategoryProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("category", models.CharField(
                    help_text="Exercise category slug (matches Exercise.category)",
                    max_length=50,
                )),
                ("easy_cleared", models.BooleanField(default=False)),
                ("medium_cleared", models.BooleanField(default=False)),
                ("hard_cleared", models.BooleanField(default=False)),
                ("lesson", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="category_progress",
                    to="content.lesson",
                )),
                ("student", models.ForeignKey(
                    limit_choices_to={"user_type": "student"},
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="category_progress",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                "db_table": "category_progress",
            },
        ),
        migrations.AlterUniqueTogether(
            name="categoryprogress",
            unique_together={("student", "lesson", "category")},
        ),
    ]
