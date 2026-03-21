"""
Migration: Introduce Topic model between Unit and Lesson.

CategoryProgress FK change is handled separately in
progress/migrations/0004_categoryprogress_topic.py
"""
import django.db.models.deletion
from django.db import migrations, models


def migrate_to_topics(apps, schema_editor):
    """
    For every existing Lesson, create a 1-to-1 Topic in the same Unit,
    then point all related objects (Exercise, Test) to that topic.
    CategoryProgress is handled in the progress app migration.
    """
    Lesson = apps.get_model("content", "Lesson")
    Topic = apps.get_model("content", "Topic")
    Exercise = apps.get_model("content", "Exercise")
    Test = apps.get_model("content", "Test")

    lesson_topic_map = {}

    for lesson in Lesson.objects.select_related("unit").order_by("unit", "order"):
        topic = Topic.objects.create(
            unit=lesson.unit,
            order=lesson.order,
            title=lesson.title,
            description="",
            is_published=lesson.is_published,
            practice_minimum=lesson.practice_minimum,
        )
        lesson.topic = topic
        lesson.save(update_fields=["topic"])
        lesson_topic_map[lesson.id] = topic

    # Move exercises
    for exercise in Exercise.objects.all():
        exercise.topic = lesson_topic_map[exercise.lesson_id]
        exercise.save(update_fields=["topic"])

    # Move lesson-scoped tests
    for test in Test.objects.filter(scope="lesson"):
        test.topic = lesson_topic_map[test.lesson_id]
        test.scope = "topic"
        test.save(update_fields=["topic", "scope"])


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0007_multi_fill_blank_type"),
    ]

    operations = [
        # ── Step 1: Create topics table ───────────────────────────────────
        migrations.CreateModel(
            name="Topic",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveSmallIntegerField()),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("is_published", models.BooleanField(default=False)),
                ("practice_minimum", models.PositiveSmallIntegerField(default=5)),
                (
                    "unit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="topics",
                        to="content.unit",
                    ),
                ),
            ],
            options={"db_table": "topics", "ordering": ["unit", "order"]},
        ),
        migrations.AlterUniqueTogether(
            name="topic",
            unique_together={("unit", "order")},
        ),

        # ── Step 2: Add nullable topic FK to Lesson ───────────────────────
        migrations.AddField(
            model_name="lesson",
            name="topic",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="lessons",
                to="content.topic",
            ),
        ),

        # ── Step 3: Add nullable topic FK to Exercise ─────────────────────
        migrations.AddField(
            model_name="exercise",
            name="topic",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="exercises",
                to="content.topic",
            ),
        ),

        # ── Step 4: Add nullable topic FK to Test ─────────────────────────
        migrations.AddField(
            model_name="test",
            name="topic",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="test",
                to="content.topic",
            ),
        ),

        # ── Step 4b: Drop old constraint BEFORE data migration ────────────
        # The old constraint only allows scope="lesson" or scope="unit".
        # The data migration sets scope="topic", which would violate it.
        migrations.RemoveConstraint(model_name="test", name="test_scope_consistency"),

        # ── Step 5: Data migration ─────────────────────────────────────────
        migrations.RunPython(
            migrate_to_topics,
            reverse_code=migrations.RunPython.noop,
        ),

        # ── Step 6: Make topic FKs non-nullable ───────────────────────────
        migrations.AlterField(
            model_name="lesson",
            name="topic",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="lessons",
                to="content.topic",
            ),
        ),
        migrations.AlterField(
            model_name="exercise",
            name="topic",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="exercises",
                to="content.topic",
            ),
        ),

        # ── Step 7: Remove old FKs / fields from Lesson and Exercise ──────
        # Clear unique_together BEFORE dropping the unit field it references
        migrations.AlterUniqueTogether(
            name="lesson",
            unique_together=set(),
        ),
        migrations.RemoveField(model_name="lesson", name="unit"),
        migrations.RemoveField(model_name="lesson", name="practice_minimum"),
        migrations.RemoveField(model_name="exercise", name="lesson"),

        # ── Step 8: Update Test scope choices + remove old lesson FK ──────
        migrations.AlterField(
            model_name="test",
            name="scope",
            field=models.CharField(
                max_length=10,
                choices=[("topic", "Topic Test"), ("unit", "Unit Test")],
                default="unit",
            ),
        ),
        migrations.RemoveField(model_name="test", name="lesson"),
        migrations.AddConstraint(
            model_name="test",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(scope="topic", topic__isnull=False, unit__isnull=True) |
                    models.Q(scope="unit", unit__isnull=False, topic__isnull=True)
                ),
                name="test_scope_consistency",
            ),
        ),

        # ── Step 9: Set new unique_together on Lesson ────────────────────
        migrations.AlterUniqueTogether(
            name="lesson",
            unique_together={("topic", "order")},
        ),
    ]