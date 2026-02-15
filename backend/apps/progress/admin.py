from django.contrib import admin

from .models import ClassroomPace, ExerciseAttempt, LessonProgress, Streak, TestAttempt


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "status", "completed_at")
    list_filter = ("status",)


@admin.register(ExerciseAttempt)
class ExerciseAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "exercise", "is_correct", "attempted_at")
    list_filter = ("is_correct",)


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "test", "score", "passed", "started_at")
    list_filter = ("passed",)


@admin.register(ClassroomPace)
class ClassroomPaceAdmin(admin.ModelAdmin):
    list_display = ("teacher", "unit", "unlock_date")


@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ("student", "current_streak", "longest_streak", "last_active_date")
