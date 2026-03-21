import json

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from .models import Exercise, GlossaryTerm, Grade, Lesson, Test, Topic, Unit


# ─── Grade ────────────────────────────────────────────────────────────────────

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("number", "name", "is_active", "unit_count", "topic_count")
    list_editable = ("is_active",)

    @admin.display(description="Units")
    def unit_count(self, obj):
        return obj.units.count()

    @admin.display(description="Topics")
    def topic_count(self, obj):
        return Topic.objects.filter(unit__grade=obj).count()


# ─── Unit ─────────────────────────────────────────────────────────────────────

class TopicInline(admin.TabularInline):
    model = Topic
    extra = 0
    fields = ("order", "title", "is_published", "practice_minimum")
    ordering = ("order",)
    show_change_link = True


class UnitTestInline(admin.StackedInline):
    model = Test
    extra = 0
    max_num = 1
    fk_name = "unit"


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "grade",
        "is_published",
        "topic_count",
        "has_test",
        "recommended_unlock_date",
    )
    list_filter = ("grade", "is_published")
    list_editable = ("is_published", "recommended_unlock_date")
    inlines = [TopicInline, UnitTestInline]
    fieldsets = (
        (None, {"fields": ("grade", "order", "title")}),
        ("Description", {"fields": ("description",), "classes": ("collapse",)}),
        ("Publishing", {"fields": ("is_published", "recommended_unlock_date")}),
    )

    @admin.display(description="Topics")
    def topic_count(self, obj):
        total = obj.topics.count()
        published = obj.topics.filter(is_published=True).count()
        return f"{published}/{total}"

    @admin.display(description="Test", boolean=True)
    def has_test(self, obj):
        return hasattr(obj, "test")


# ─── Topic ────────────────────────────────────────────────────────────────────

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("order", "title", "is_published")
    ordering = ("order",)
    show_change_link = True


class TopicTestInline(admin.StackedInline):
    model = Test
    extra = 0
    max_num = 1
    fk_name = "topic"
    fields = ("scope", "pass_threshold", "time_limit_minutes", "retry_practice_count", "composition", "is_published")


class ExerciseInline(admin.StackedInline):
    model = Exercise
    extra = 0
    fields = ("exercise_type", "difficulty", "category", "template", "is_active")
    classes = ("collapse",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "unit",
        "is_published",
        "lesson_count",
        "exercise_count",
        "practice_minimum",
        "has_test",
    )
    list_filter = ("unit__grade", "unit", "is_published")
    list_editable = ("is_published",)
    search_fields = ("title",)
    inlines = [LessonInline, ExerciseInline, TopicTestInline]
    save_on_top = True

    fieldsets = (
        (None, {"fields": ("unit", "order", "title")}),
        ("Description", {"fields": ("description",), "classes": ("collapse",)}),
        ("Settings", {"fields": ("is_published", "practice_minimum")}),
    )

    @admin.display(description="Lessons")
    def lesson_count(self, obj):
        total = obj.lessons.count()
        published = obj.lessons.filter(is_published=True).count()
        return f"{published}/{total}"

    @admin.display(description="Exercises")
    def exercise_count(self, obj):
        total = obj.exercises.count()
        active = obj.exercises.filter(is_active=True).count()
        return f"{active}/{total}"

    @admin.display(description="Test", boolean=True)
    def has_test(self, obj):
        return hasattr(obj, "test")


# ─── Lesson ───────────────────────────────────────────────────────────────────

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("__str__", "topic_display", "is_published", "updated_at")
    list_filter = ("topic__unit__grade", "topic__unit", "is_published")
    list_editable = ("is_published",)
    search_fields = ("title",)
    save_on_top = True

    fieldsets = (
        (None, {"fields": ("topic", "order", "title")}),
        ("Summary", {"fields": ("summary",)}),
        (
            "Lesson Content",
            {
                "fields": ("blocks",),
                "description": (
                    "Write lesson content here. Use $expression$ for inline math "
                    "and $$expression$$ for display math (KaTeX syntax)."
                ),
            },
        ),
        ("Settings", {"fields": ("is_published",)}),
    )

    class Media:
        js = ("admin/js/katex_preview.js",)

    @admin.display(description="Topic")
    def topic_display(self, obj):
        return str(obj.topic)


# ─── Exercise ─────────────────────────────────────────────────────────────────

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = (
        "exercise_title",
        "exercise_type",
        "difficulty",
        "category",
        "is_active",
        "topic_display",
        "preview_link",
    )
    list_filter = ("exercise_type", "difficulty", "is_active", "topic__unit__grade")
    search_fields = ("topic__title", "category")
    readonly_fields = ("preview_link",)

    fieldsets = (
        (None, {"fields": ("topic", "exercise_type", "difficulty", "category")}),
        (
            "Exercise Template (JSON)",
            {
                "fields": ("template",),
                "description": format_html(
                    "<strong>Template format:</strong><br>"
                    '<code>{{"question": "Calculează: ${{a}} + {{b}}$ = ?", '
                    '"params": {{"a": {{"type": "randint", "min": 1, "max": 50}}, '
                    '"b": {{"type": "randint", "min": 1, "max": 50}}}}, '
                    '"answer_expr": "{{a}} + {{b}}"}}</code>'
                ),
            },
        ),
        (
            "Preview",
            {
                "fields": ("preview_link",),
                "description": "Opens the exercise in the frontend with live KaTeX rendering.",
            },
        ),
        ("Status", {"fields": ("is_active",)}),
    )

    @admin.display(description="Exercise")
    def exercise_title(self, obj):
        title = obj.template.get("title") if isinstance(obj.template, dict) else None
        if title:
            return title
        cat = f" — {obj.category}" if obj.category else ""
        return f"{obj.exercise_type} / {obj.difficulty}{cat}"

    @admin.display(description="Topic")
    def topic_display(self, obj):
        return obj.topic.title if obj.topic_id else "—"

    @admin.display(description="Preview")
    def preview_link(self, obj):
        if not obj.pk:
            return "Salvează exercițiul mai întâi."
        url = f"{settings.FRONTEND_URL}/admin-preview/exercise/{obj.pk}"
        return format_html('<a href="{}" target="_blank">🔍 Preview</a>', url)
