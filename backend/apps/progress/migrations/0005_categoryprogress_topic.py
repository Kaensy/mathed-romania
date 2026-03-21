"""
Migration: Move CategoryProgress.lesson FK → CategoryProgress.topic FK.
Depends on content 0008_topic being applied first (Topic model must exist).
"""
import django.db.models.deletion
from django.db import migrations, models


def migrate_categoryprogress_to_topic(apps, schema_editor):
    CategoryProgress = apps.get_model("progress", "CategoryProgress")
    Lesson = apps.get_model("content", "Lesson")

    lesson_to_topic = {lesson.id: lesson.topic_id for lesson in Lesson.objects.order_by("id")}

    for cp in CategoryProgress.objects.all():
        topic_id = lesson_to_topic.get(cp.lesson_id)
        if topic_id:
            cp.topic_id = topic_id
            cp.save(update_fields=["topic"])


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0008_topic"),
        ("progress", "0003_categoryprogress_session_id"),
    ]

    operations = [
        # ── Step 1: Add nullable topic FK ────────────────────────────────
        migrations.AddField(
            model_name="categoryprogress",
            name="topic",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="category_progress",
                to="content.topic",
            ),
        ),

        # ── Step 2: Data migration ────────────────────────────────────────
        migrations.RunPython(
            migrate_categoryprogress_to_topic,
            reverse_code=migrations.RunPython.noop,
        ),

        # ── Step 3: Make topic FK non-nullable ────────────────────────────
        migrations.AlterField(
            model_name="categoryprogress",
            name="topic",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="category_progress",
                to="content.topic",
            ),
        ),

        # ── Step 4: Clear old unique_together BEFORE removing lesson FK ───
        migrations.AlterUniqueTogether(
            name="categoryprogress",
            unique_together=set(),
        ),

        # ── Step 5: Remove old lesson FK ─────────────────────────────────
        migrations.RemoveField(
            model_name="categoryprogress",
            name="lesson",
        ),

        # ── Step 6: Set new unique_together ───────────────────────────────
        migrations.AlterUniqueTogether(
            name="categoryprogress",
            unique_together={("student", "topic", "category")},
        ),
    ]