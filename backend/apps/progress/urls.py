from django.urls import path

from .views import (
    DashboardView,
    ExerciseAttemptView,
    ExercisesOverviewView,
    ExercisePreviewInstanceView,
    LessonCompleteView,
    LessonOpenView,
    TestsOverviewView,
    TestStartView,
    TestAnswerView,
    TestFinishView,
    TestResultView,
    TopicCategoriesView,
    TopicPracticeView,
)

urlpatterns = [
    # Lesson progress (content reading — still per-lesson)
    path("lessons/<int:lesson_id>/open/", LessonOpenView.as_view(), name="lesson_open"),
    path("lessons/<int:lesson_id>/complete/", LessonCompleteView.as_view(), name="lesson_complete"),

    # Topic practice & categories
    path("topics/<int:topic_id>/practice/", TopicPracticeView.as_view(), name="topic_practice"),
    path("topics/<int:topic_id>/categories/", TopicCategoriesView.as_view(), name="topic_categories"),

    # Exercise attempt submission
    path("exercises/attempt/", ExerciseAttemptView.as_view(), name="exercise_attempt"),
    path("exercises/<int:exercise_id>/preview-instance/", ExercisePreviewInstanceView.as_view(), name="exercise_preview_instance"),

    # Overview pages
    path("exercises-overview/", ExercisesOverviewView.as_view(), name="exercises_overview"),
    path("tests-overview/", TestsOverviewView.as_view(), name="tests_overview"),

    # Test session
    path("tests/<int:test_id>/start/", TestStartView.as_view(), name="test_start"),
    path("tests/<int:test_id>/answer/", TestAnswerView.as_view(), name="test_answer"),
    path("tests/<int:test_id>/finish/", TestFinishView.as_view(), name="test_finish"),
    path("tests/<int:test_id>/result/", TestResultView.as_view(), name="test_result"),

    # Dashboard
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
