"""
Category display-name registry — slug → Romanian label.

Single source of truth for the human-readable name of every exercise
category. Surfaces (dashboard "Recomandat pentru tine", profile weak
categories, post-test breakdown, /exerciții topic-detail, test history)
all read through `get_display_name`.

Adding a new category: add the slug here at the same time you write
the exercise template file. The exercise file's docstring `Label (RO):`
line is informational; this registry is what surfaces actually consume.

If a slug is missing, `get_display_name` falls back to the slug itself
so nothing crashes — but the slug will visibly leak, which is the
signal to add an entry.
"""

CATEGORY_DISPLAY_NAMES: dict[str, str] = {
    # 1.1 — Mulțimea numerelor naturale
    "number_to_words":            "Scriere în cuvinte",
    "words_to_number":            "Scriere în cifre",
    "counting_interval":          "Numărare în interval",
    "digit_rules":                "Determinare cifre după reguli",
    "canonical_form":             "Formă canonică",

    # 1.2 — Compararea numerelor
    "comparing_numbers":          "Comparare numere",
    "ordering_numbers":           "Ordonare numere",

    # 1.3 — Rotunjire
    "rounding":                   "Rotunjire",

    # 1.4 — Adunarea
    "addition_compute":           "Calcul cu adunări",
    "find_x_addition":            "Aflarea necunoscutei",
    "arithmetic_sequence":        "Șir aritmetic",
    "gauss_sum":                  "Suma lui Gauss",

    # 1.5 — Scăderea
    "subtraction_compute":        "Calcul cu scăderi",
    "find_x_subtraction":         "Aflarea necunoscutei (scădere)",
    "sum_and_difference":         "Suma și diferența",

    # 1.6 — Înmulțirea
    "multiplication_compute":     "Calcul cu înmulțiri",
    "find_x_multiplication":      "Aflarea necunoscutei (înmulțire)",
    "common_factor":              "Factor comun",
    "last_digit":                 "Ultima cifră",
    "distributivity":             "Distributivitate",

    # 1.7 — Împărțirea
    "division_compute":           "Calcul cu împărțiri",
    "division_remainder_compute": "Calcul cu rest",
    "find_x_division":            "Aflarea necunoscutei (împărțire)",
    "find_from_division_theorem": "Teorema împărțirii cu rest",
    "division_exact":             "Împărțire exactă",
    "division_remainder":         "Împărțire cu rest",

    # 1.8 — Puteri
    "power_notation":             "Notația puterii",
    "power_compute":              "Calcul cu puteri",
    "power_rules_simplify":       "Scriere ca o singură putere",
    "power_common_factor":        "Factor comun cu puteri",
    "find_x_powers":              "Aflarea necunoscutei (puteri)",
    "power_last_digit":           "Ultima cifră a unei puteri",
    "power_sum_telescope":        "Sume de puteri consecutive",
    "power_compare":              "Compararea puterilor",
    "power_order":                "Ordonarea puterilor",
    "perfect_square_identify":    "Pătrate perfecte — recunoaștere",
    "perfect_square_between":     "Pătrate perfecte consecutive",

    # 1.9 — Baze de numerație
    "convert_to_base10":          "Conversie spre baza 10",
    "convert_from_base10":        "Conversie din baza 10",
    "mixed_base_compute":         "Calcul cu baze diferite",

    # 1.10 — Ordinea operațiilor
    "order_of_ops_basic":         "Ordinea operațiilor — fără paranteze",
    "order_of_ops_parens":        "Ordinea operațiilor — cu paranteze",
    "order_of_ops_nested":        "Ordinea operațiilor — paranteze imbricate",
}


def get_display_name(slug: str) -> str:
    """Return the Romanian display name for a category slug.

    Falls back to the slug itself if unknown — surfaces won't crash,
    and the visible slug signals a missing registry entry.
    """
    if not slug:
        return slug
    return CATEGORY_DISPLAY_NAMES.get(slug, slug)
