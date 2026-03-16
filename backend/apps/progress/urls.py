from django.urls import path

from .views import (
    DashboardView,
    ExerciseAttemptView,
    LessonCompleteView,
    LessonOpenView,
    LessonPracticeView,
    TestStartView,
    TestAnswerView,
    TestFinishView,
    TestResultView,
    LessonCategoriesView,
)

urlpatterns = [
    # Lesson progress
    path("lessons/<int:lesson_id>/open/", LessonOpenView.as_view(), name="lesson_open"),
    path("lessons/<int:lesson_id>/complete/", LessonCompleteView.as_view(), name="lesson_complete"),
    path("lessons/<int:lesson_id>/categories/", LessonCategoriesView.as_view(), name="lesson_categories"),

    # Practice
    path("lessons/<int:lesson_id>/practice/", LessonPracticeView.as_view(), name="lesson_practice"),

    # Attempt submission (practice)
    path("exercises/attempt/", ExerciseAttemptView.as_view(), name="exercise_attempt"),

    # Test session
    path("tests/<int:test_id>/start/", TestStartView.as_view(), name="test_start"),
    path("tests/<int:test_id>/answer/", TestAnswerView.as_view(), name="test_answer"),
    path("tests/<int:test_id>/finish/", TestFinishView.as_view(), name="test_finish"),
    path("tests/<int:test_id>/result/", TestResultView.as_view(), name="test_result"),

    # Dashboard
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]