import json

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from .models import Exercise, GlossaryTerm, Grade, Lesson, Test, Unit


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("number", "name", "is_active", "unit_count", "lesson_count")
    list_editable = ("is_active",)

    @admin.display(description="Units")
    def unit_count(self, obj):
        return obj.units.count()

    @admin.display(description="Total Lessons")
    def lesson_count(self, obj):
        return Lesson.objects.filter(unit__grade=obj).count()


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("order", "title", "is_published", "practice_minimum")
    ordering = ("order",)
    show_change_link = True


class TestInline(admin.StackedInline):
    model = Test
    extra = 0
    max_num = 1


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "grade",
        "is_published",
        "lesson_count",
        "has_test",
        "recommended_unlock_date",
    )
    list_filter = ("grade", "is_published")
    list_editable = ("is_published", "recommended_unlock_date")
    inlines = [LessonInline, TestInline]
    fieldsets = (
        (None, {"fields": ("grade", "order", "title")}),
        ("Description", {"fields": ("description",), "classes": ("collapse",)}),
        ("Publishing", {"fields": ("is_published", "recommended_unlock_date")}),
    )

    @admin.display(description="Lessons")
    def lesson_count(self, obj):
        count = obj.lessons.count()
        published = obj.lessons.filter(is_published=True).count()
        return f"{published}/{count}"

    @admin.display(description="Test", boolean=True)
    def has_test(self, obj):
        return hasattr(obj, "test")


class ExerciseInline(admin.StackedInline):
    model = Exercise
    extra = 0
    fields = ("exercise_type", "difficulty", "template", "is_active")
    classes = ("collapse",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("__str__", "unit_display", "is_published", "exercise_count", "practice_minimum", "updated_at")
    list_filter = ("unit__grade", "unit", "is_published")
    list_editable = ("is_published",)
    search_fields = ("title",)
    inlines = [ExerciseInline]
    save_on_top = True

    fieldsets = (
        (None, {"fields": ("unit", "order", "title")}),
        ("Summary", {"fields": ("summary",)}),
        (
            "Lesson Content",
            {
                "fields": ("blocks",),
                "description": (
                    "Write lesson content here. Use $expression$ for inline math "
                    "and $$expression$$ for display math (KaTeX syntax). "
                    "Click the preview button below the editor to see rendered math."
                ),
            },
        ),
        ("Settings", {"fields": ("is_published", "practice_minimum")}),
    )

    class Media:
        js = ("admin/js/katex_preview.js",)

    @admin.display(description="Unit")
    def unit_display(self, obj):
        return f"{obj.unit.grade.number}.{obj.unit.order}"

    @admin.display(description="Exercises")
    def exercise_count(self, obj):
        count = obj.exercises.count()
        active = obj.exercises.filter(is_active=True).count()
        return f"{active}/{count}"


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("exercise_title", "exercise_type", "difficulty", "category", "is_active", "lesson_display", "preview_link")
    list_filter = ("exercise_type", "difficulty", "is_active", "lesson__unit__grade")
    search_fields = ("lesson__title", "category")
    readonly_fields = ("preview_link",)

    fieldsets = (
        (None, {"fields": ("lesson", "exercise_type", "difficulty", "category")}),
        (
            "Exercise Template (JSON)",
            {
                "fields": ("template",),
                "description": format_html(
                    "<strong>Template format examples:</strong><br><br>"
                    "<strong>Fill in the Blank:</strong><br>"
                    '<code>{{"question": "Calculează: ${{a}} + {{b}}$ = ?", "params": {{"a": {{"type": "randint", "min": 1, "max": 50}}, "b": {{"type": "randint", "min": 1, "max": 50}}}}, '
                    '"answer_expr": "{{a}} + {{b}}"}}</code>'
                ),
            },
        ),
        (
            "Preview",
            {
                "fields": ("preview_link",),
                "description": "Opens the exercise in the frontend with real KaTeX rendering and live answer checking.",
            },
        ),
        ("Status", {"fields": ("is_active",)}),
    )

    @admin.display(description="Preview")
    def preview_link(self, obj):
        if not obj.pk:
            return "Salvează exercițiul mai întâi."
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        url = f"{frontend_url}/admin-preview/exercise/{obj.pk}"
        return format_html(
            '<a href="{}" target="_blank" '
            'style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;'
            'background:#4f46e5;color:#fff;border-radius:6px;font-size:12px;text-decoration:none;font-weight:600;">'
            "🔍 Preview în aplicație</a>",
            url,
        )

    @admin.display(description="Title")
    def exercise_title(self, obj):
        return obj.template.get("title") or f"({obj.exercise_type}) — {obj.lesson.title}"

    @admin.display(description="Lesson")
    def lesson_display(self, obj):
        return obj.lesson.title


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("__str__", "scope", "pass_threshold_display", "time_limit_display", "is_published")
    list_filter = ("scope", "is_published")
    list_editable = ("is_published",)

    @admin.display(description="Pass %")
    def pass_threshold_display(self, obj):
        return f"{obj.pass_threshold}%"

    @admin.display(description="Time Limit")
    def time_limit_display(self, obj):
        if obj.time_limit_minutes:
            return f"{obj.time_limit_minutes} min"
        return "Untimed"


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ("term", "unit", "lesson", "created_at")
    list_filter = ("unit__grade", "unit")
    search_fields = ("term", "definition")
