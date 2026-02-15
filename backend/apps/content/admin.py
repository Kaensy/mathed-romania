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
    show_change_link = True  # Link to full lesson edit page


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
    """Stacked inline gives more room for the JSON template field."""

    model = Exercise
    extra = 0
    fields = ("exercise_type", "difficulty", "template", "is_active")
    classes = ("collapse",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("__str__", "unit_display", "is_published", "exercise_count", "practice_minimum", "updated_at")
    list_filter = ("unit__grade", "unit", "is_published")
    list_editable = ("is_published",)
    search_fields = ("title", "content")
    inlines = [ExerciseInline]
    save_on_top = True  # Save button at top too — useful for long content

    fieldsets = (
        (None, {"fields": ("unit", "order", "title")}),
        ("Summary", {"fields": ("summary",)}),
        (
            "Lesson Content",
            {
                "fields": ("content",),
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
    list_display = ("__str__", "exercise_type", "difficulty", "is_active", "lesson_display")
    list_filter = ("exercise_type", "difficulty", "is_active", "lesson__unit__grade")
    search_fields = ("lesson__title",)

    fieldsets = (
        (None, {"fields": ("lesson", "exercise_type", "difficulty")}),
        (
            "Exercise Template (JSON)",
            {
                "fields": ("template",),
                "description": format_html(
                    "<strong>Template format examples:</strong><br><br>"
                    "<strong>Multiple Choice:</strong><br>"
                    '<code>{{"question": "Cât este $2 + 3$?", "choices": ["4", "5", "6", "7"], '
                    '"correct_index": 1}}</code><br><br>'
                    "<strong>Fill in the Blank:</strong><br>"
                    '<code>{{"question": "Calculează: $a + b$ = ?", "params": {{"a": [1, 50], "b": [1, 50]}}, '
                    '"answer_formula": "a + b"}}</code><br><br>'
                    "<strong>Expression Input:</strong><br>"
                    '<code>{{"question": "Simplifică fracția $\\\\frac{{12}}{{8}}$", '
                    '"correct_answer": "\\\\frac{{3}}{{2}}"}}</code><br><br>'
                    "<strong>True/False:</strong><br>"
                    '<code>{{"statement": "$15$ este număr prim", "correct_answer": false}}</code>'
                ),
            },
        ),
        ("Status", {"fields": ("is_active",)}),
    )

    @admin.display(description="Lesson")
    def lesson_display(self, obj):
        return obj.lesson.title


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "pass_threshold_display",
        "time_limit_display",
        "exercise_count",
        "retry_practice_count",
        "is_published",
    )
    list_filter = ("is_published", "unit__grade")
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
