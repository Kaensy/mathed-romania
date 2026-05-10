"""
Pet species catalog.

Declarative — adding a species is a code edit, not a migration. Pet.kind
is a free-form CharField; choices are derived from PET_SPECIES at import
time so the admin/forms list stays in sync.

GRADE_DEFAULT_SPECIES picks the default species for each grade. New
grades register here once their content ships; until they do,
`default_species_for_grade` returns None and Pet auto-creation skips.
"""
from typing import TypedDict


class SpeciesDef(TypedDict):
    display_name: str
    default_name: str


PET_SPECIES: dict[str, SpeciesDef] = {
    "pui_de_lup": {
        "display_name": "Pui de lup",
        "default_name": "Lupul",
    },
}


GRADE_DEFAULT_SPECIES: dict[int, str] = {
    5: "pui_de_lup",
}


def default_species_for_grade(grade) -> str | None:
    """Return the default pet kind for a `content.Grade` row.

    Returns None when the grade has no entry in GRADE_DEFAULT_SPECIES —
    callers should treat this as "skip pet creation for this grade".
    """
    if grade is None:
        return None
    return GRADE_DEFAULT_SPECIES.get(grade.number)


def species_choices() -> list[tuple[str, str]]:
    """Choices tuple for the Pet.pet_kind CharField."""
    return [(kind, defn["display_name"]) for kind, defn in PET_SPECIES.items()]
