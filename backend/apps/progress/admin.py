from django.contrib import admin

from .models import (
    Achievement,
    CategoryProgress,
    ClassroomPace,
    DailyChallengeProgress,
    DailyTestSession,
    ExerciseAttempt,
    LessonProgress,
    QuestAssignment,
    Streak,
    StreakActivity,
    TestAttempt,
)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "status", "completed_at")
    list_filter = ("status",)


@admin.register(ExerciseAttempt)
class ExerciseAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "exercise", "is_correct", "session_id", "attempted_at")
    list_filter = ("is_correct",)


@admin.register(CategoryProgress)
class CategoryProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "topic", "category", "easy_cleared", "medium_cleared", "hard_cleared")
    list_filter = ("topic", "easy_cleared", "medium_cleared", "hard_cleared")


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "test", "score", "passed", "started_at")
    list_filter = ("passed",)


@admin.register(ClassroomPace)
class ClassroomPaceAdmin(admin.ModelAdmin):
    list_display = ("teacher", "unit", "unlock_date")


@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ("student", "current_streak", "longest_streak", "last_active_date", "freeze_count")


@admin.register(StreakActivity)
class StreakActivityAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "activity_type")
    list_filter = ("activity_type",)


@admin.register(DailyTestSession)
class DailyTestSessionAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "is_completed", "completed_at")
    list_filter = ("is_completed", "date")
    readonly_fields = ("exercise_instances", "completed_indices", "completed_at", "created_at")


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("student", "badge_key", "earned_at")
    list_filter = ("badge_key",)


@admin.register(QuestAssignment)
class QuestAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "student", "quest_slug", "cadence", "period_key",
        "progress", "target", "status",
    )
    list_filter = ("cadence", "status", "quest_slug")
    readonly_fields = ("created_at", "completed_at", "claimed_at")


@admin.register(DailyChallengeProgress)
class DailyChallengeProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "points", "claimed_thresholds")
    list_filter = ("date",)
    readonly_fields = ("created_at", "updated_at")
