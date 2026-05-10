from django.urls import path

from .views import PetMeView

urlpatterns = [
    path("me/", PetMeView.as_view(), name="pet_me"),
]
