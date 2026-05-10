"""Pet serializers — output shape and PATCH name validation."""
import re

from rest_framework import serializers

from .levels import level_for_xp, xp_to_next_level
from .species import PET_SPECIES

# Letters (incl. diacritics), spaces, and hyphens. Strips emoji / digits /
# punctuation. Anchored to full match so any disallowed char fails.
_NAME_ALLOWED = re.compile(r"^[^\W\d_]+(?:[ \-][^\W\d_]+)*$", re.UNICODE)
_NAME_MAX_LEN = 30


def _species_default_name(kind: str) -> str:
    defn = PET_SPECIES.get(kind)
    return defn["default_name"] if defn else kind


def _species_display_name(kind: str) -> str:
    defn = PET_SPECIES.get(kind)
    return defn["display_name"] if defn else kind


class PetSerializer(serializers.Serializer):
    """Read-only output shape for GET /pets/me/."""

    id = serializers.IntegerField(read_only=True)
    pet_kind = serializers.CharField(read_only=True)
    kind_display = serializers.SerializerMethodField()
    name = serializers.CharField(read_only=True)
    display_name = serializers.SerializerMethodField()
    pet_xp = serializers.IntegerField(read_only=True)
    level = serializers.SerializerMethodField()
    xp_to_next_level = serializers.SerializerMethodField()
    grade_number = serializers.IntegerField(source="grade.number", read_only=True)
    total_xp = serializers.SerializerMethodField()

    def get_kind_display(self, pet) -> str:
        return _species_display_name(pet.pet_kind)

    def get_display_name(self, pet) -> str:
        return pet.name or _species_default_name(pet.pet_kind)

    def get_level(self, pet) -> int:
        return level_for_xp(pet.pet_xp)

    def get_xp_to_next_level(self, pet) -> int:
        return xp_to_next_level(pet.pet_xp)

    def get_total_xp(self, pet) -> int:
        return pet.student.total_xp


class PetRenameSerializer(serializers.Serializer):
    """Validates the `name` field on PATCH /pets/me/.

    Whitespace is trimmed first; an empty result clears the name (the
    pet falls back to the species default in `display_name`). Otherwise
    enforces: <=30 chars, only Unicode letters, spaces, and hyphens.
    """

    name = serializers.CharField(
        allow_blank=True, max_length=_NAME_MAX_LEN, trim_whitespace=False,
    )

    def validate_name(self, value: str) -> str:
        stripped = value.strip()
        if stripped == "":
            return ""
        if len(stripped) > _NAME_MAX_LEN:
            raise serializers.ValidationError(
                f"Numele are maxim {_NAME_MAX_LEN} caractere."
            )
        if not _NAME_ALLOWED.match(stripped):
            raise serializers.ValidationError(
                "Numele poate conține doar litere, spații și liniuțe."
            )
        return stripped
