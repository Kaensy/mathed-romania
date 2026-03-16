"""
Serializers for the progress API.
"""
from rest_framework import serializers

from apps.progress.models import ExerciseAttempt, LessonProgress


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ["lesson_id", "status", "completed_at", "time_spent_seconds"]


class ExerciseAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseAttempt
        fields = ["id", "exercise_id", "answer", "is_correct", "attempted_at"]


class AttemptSubmitSerializer(serializers.Serializer):
    """Validates incoming attempt submission from the frontend."""
    exercise_id = serializers.IntegerField()
    instance_token = serializers.CharField()
    answer = serializers.JSONField()  # string for fill_blank/comparison/mc, list for drag_order


class DashboardSerializer(serializers.Serializer):
    """Read-only summary stats for the student dashboard."""
    total_lessons = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    in_progress_lessons = serializers.IntegerField()
    total_attempts = serializers.IntegerField()
    correct_attempts = serializers.IntegerField()
    accuracy_percent = serializers.FloatField()
    units = serializers.ListField(child=serializers.DictField())
