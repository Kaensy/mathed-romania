from django.contrib import admin

from .models import Exercise, Grade, Lesson, Test, Unit


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("number", "name", "is_active")


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("order", "title", "is_published", "practice_minimum")
    ordering = ("order",)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("__str__", "grade", "is_published", "recommended_unlock_date")
    list_filter = ("grade", "is_published")
    inlines = [LessonInline]


class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 0
    fields = ("exercise_type", "difficulty", "is_active")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_published", "practice_minimum", "updated_at")
    list_filter = ("unit__grade", "is_published")
    search_fields = ("title",)
    inlines = [ExerciseInline]


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("__str__", "exercise_type", "difficulty", "is_active")
    list_filter = ("exercise_type", "difficulty", "is_active")


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("__str__", "pass_threshold", "time_limit_minutes", "exercise_count", "is_published")
    list_filter = ("is_published",)
