from django.urls import path

from .views import (
    GlossaryListView,
    GradeDetailView,
    GradeListView,
    LessonDetailView,
    UnitDetailView,
)

urlpatterns = [
    path("grades/", GradeListView.as_view(), name="grade_list"),
    path("grades/<int:grade_number>/", GradeDetailView.as_view(), name="grade_detail"),
    path("units/<int:unit_id>/", UnitDetailView.as_view(), name="unit_detail"),
    path("lessons/<int:lesson_id>/", LessonDetailView.as_view(), name="lesson_detail"),
    path("glossary/", GlossaryListView.as_view(), name="glossary_list"),
]
