"""Pet API views.

Endpoints (student-only):
  GET   /api/v1/pets/me/   — current-grade pet, with derived fields.
  PATCH /api/v1/pets/me/   — rename (or clear-to-default).
"""
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Grade
from apps.users.models import StudentProfile

from .models import Pet
from .serializers import PetRenameSerializer, PetSerializer


def _student_pet_for_current_grade(user):
    """Return (pet, error_response). On success, error_response is None."""
    if not getattr(user, "is_student", False):
        return None, Response(
            {"error": "Doar elevii au animale de companie."},
            status=status.HTTP_403_FORBIDDEN,
        )

    profile = (
        StudentProfile.objects
        .select_related("user")
        .filter(user=user)
        .first()
    )
    if profile is None:
        return None, Response(
            {"error": "Profil de elev inexistent."},
            status=status.HTTP_404_NOT_FOUND,
        )

    grade = Grade.objects.filter(number=profile.grade).first()
    if grade is None:
        return None, Response(
            {"error": "Clasa elevului nu este configurată."},
            status=status.HTTP_404_NOT_FOUND,
        )

    pet = (
        Pet.objects
        .select_related("student", "grade")
        .filter(student=profile, grade=grade)
        .first()
    )
    if pet is None:
        return None, Response(
            {"error": "Nu există un animal pentru clasa ta."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return pet, None


class PetMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pet, err = _student_pet_for_current_grade(request.user)
        if err is not None:
            return err
        return Response(PetSerializer(pet).data)

    def patch(self, request):
        pet, err = _student_pet_for_current_grade(request.user)
        if err is not None:
            return err

        serializer = PetRenameSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        pet.name = serializer.validated_data["name"]
        pet.save(update_fields=["name"])
        return Response(PetSerializer(pet).data)
