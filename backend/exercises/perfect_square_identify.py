"""
Exercise data: perfect_square_identify
Topic 1.8 — Puterea cu exponent natural (sub-lesson C: comparare, pătrate)

Category: perfect_square_identify
Label (RO): Pătrate perfecte — recunoaștere

Tiers:
  Easy   — Single-step recognition:
             small numbers directly checked (49, 64, 72, ...)
             power with even exponent ⇒ yes
             number ending in 2/3/7/8 ⇒ no (last-digit rule)
  Medium — Rule combination:
             power with odd exponent, base rewritable as even-exp power
             product of two perfect squares
             simple rebase: 25^n, 16^n etc.
  Hard   — Compound expressions where the last-digit rule is the shortcut:
             a^m + b^n where last digit is 2/3/7/8 ⇒ not a perfect square
             a^m · b^n where both rebase to squares ⇒ yes
             sums of distinct powers with non-square last digit ⇒ no

Design notes:
  - Uses `multiple_choice` exercise type with fixed options ["Da", "Nu"].
  - `is_correct` flag on each option determines which is the right answer;
    template must set it based on the generated params.
  - Because `is_correct` cannot depend on computed params at template-
    authoring time, each template is designed around a FIXED yes-or-no
    outcome. If we want both outcomes with the same question structure,
    we split into two templates (one "yes" version, one "no" version).
  - Bounds chosen to yield unambiguous answers — no edge cases like 0^0
    or numbers where the test is misleading.

Usage:
    python manage.py load_exercises exercises.perfect_square_identify
    python manage.py load_exercises exercises.perfect_square_identify --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 8,
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Single-step recognition
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Număr mic: pătrat perfect de două cifre (Da)",
        "category": "perfect_square_identify",
        "difficulty": "easy",
        "exercise_type": "multiple_choice",
        "template": {
            "title": "Număr mic: pătrat perfect de două cifre (Da)",
            "type": "multiple_choice",
            "question": "Este numărul ${n}$ un pătrat perfect?",
            "params": {
                "k": {"type": "randint", "min": 4, "max": 9},
                "n": {"type": "computed", "expr": "{k} * {k}"},
            },
            "options": [
                {"id": "Da", "text": "Da",  "is_correct": True},
                {"id": "Nu", "text": "Nu",  "is_correct": False},
            ],
        },
    },
    {
        "name": "Număr cu ultima cifră 2, 3, 7 sau 8 (Nu)",
        "category": "perfect_square_identify",
        "difficulty": "easy",
        "exercise_type": "multiple_choice",
        "template": {
            "title": "Număr cu ultima cifră 2, 3, 7 sau 8 (Nu)",
            "type": "multiple_choice",
            "question": "Este numărul ${n}$ un pătrat perfect?",
            "params": {
                "last": {"type": "choice", "options": [2, 3, 7, 8]},
                "tens": {"type": "randint", "min": 1, "max": 99},
                "n":    {"type": "computed", "expr": "{tens} * 10 + {last}"},
            },
            "options": [
                {"id": "Da", "text": "Da",  "is_correct": False},
                {"id": "Nu", "text": "Nu",  "is_correct": True},
            ],
        },
    },
    {
        "name": "Putere cu exponent par: a^(2k) (Da)",
        "category": "perfect_square_identify",
        "difficulty": "easy",
        "exercise_type": "multiple_choice",
        "template": {
            "title": "Putere cu exponent par: a^(2k) (Da)",
            "type": "multiple_choice",
            "question": "Este numărul ${a}^{{{exp}}}$ un pătrat perfect?",
            "params": {
                "a":    {"type": "randint", "min": 2, "max": 15},
                "half": {"type": "randint", "min": 5, "max": 30},
                "exp":  {"type": "computed", "expr": "2 * {half}"},
            },
            "options": [
                {"id": "Da", "text": "Da",  "is_correct": True},
                {"id": "Nu", "text": "Nu",  "is_correct": False},
            ],
        },
    },
    {
        "name": "Putere cu bază pătrat perfect și exponent impar (Da)",
        "category": "perfect_square_identify",
        "difficulty": "easy",
        "exercise_type": "multiple_choice",
        "template": {
            "title": "Putere cu bază pătrat perfect și exponent impar (Da)",
            "type": "multiple_choice",
            "question": "Este numărul ${a}^{{{n}}}$ un pătrat perfect?",
            "params": {
                # Bases that are already perfect squares: 4, 9, 16, 25, 36, 49, 64, 81, 100.
                "a":    {"type": "choice", "options": [4, 9, 16, 25, 36, 49, 64, 81, 100]},
                "half": {"type": "randint", "min": 3, "max": 15},
                "n":    {"type": "computed", "expr": "2 * {half} + 1"},
            },
            "options": [
                {"id": "Da", "text": "Da",  "is_correct": True},
                {"id": "Nu", "text": "Nu",  "is_correct": False},
            ],
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Rule combination
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Putere cu bază non-pătrat și exponent impar (Nu)",
        "category": "perfect_square_identify",
        "difficulty": "medium",
        "exercise_type": "multiple_choice",
        "template": {
            "title": "Putere cu bază non-pătrat și exponent impar (Nu)",
            "type": "multiple_choice",
            "question": "Este numărul ${a}^{{{n}}}$ un pătrat perfect?",
            "params": {
                # Bases that are NOT perfect squares and can't be rewritten
                # as a power with an even exponent.
                "a":    {"type": "choice", "options": [2, 3, 5, 6, 7, 10, 11, 13, 15]},
                "half": {"type": "randint", "min": 3, "max": 20},
                "n":    {"type": "computed", "expr": "2 * {half} + 1"},
            },
            "options": [
                {"id": "Da", "text": "Da",  "is_correct": False},
                {"id": "Nu", "text": "Nu",  "is_correct": True},
            ],
        },
    },
    {
        "name": "Produs de două pătrate perfecte (Da)",
        "category": "perfect_square_identify",
        "difficulty": "medium",
        "exercise_type": "multiple_choice",
        "template": {
            "title": "Produs de două pătrate perfecte (Da)",
            "type": "multiple_choice",
            "question": "Este numărul ${a}^{{{m}}} \\cdot {b}^{{{n}}}$ un pătrat perfect?",
            "params": {
                "a":  {"type": "randint", "min": 2, "max": 10},
                "b":  {"type": "randint", "min": 2, "max": 10},
                "ma": {"type": "randint", "min": 3, "max": 15},
                "na": {"type": "randint", "min": 3, "max": 15},
                "m":  {"type": "computed", "expr": "2 * {ma}"},
                "n":  {"type": "computed", "expr": "2 * {na}"},
            },
            "options": [
                {"id": "Da", "text": "Da",  "is_correct": True},
                {"id": "Nu", "text": "Nu",  "is_correct": False},
            ],
        },
    },
    {
        "name": "Produs cu un factor non-pătrat (Nu)",
        "category": "perfect_square_identify",
        "difficulty": "medium",
        "exercise_type": "multiple_choice",
        "template": {
            "title": "Produs cu un factor non-pătrat (Nu)",
            "type": "multiple_choice",
            "question": "Este numărul ${a}^{{{m}}} \\cdot {b}^{{{n}}}$ un pătrat perfect?",
            "params": {
                # a^m is a perfect square (even exponent on any base),
                # b^n has odd exponent on a non-square base → overall NOT a square.
                "a":    {"type": "randint", "min": 2, "max": 10},
                "b":    {"type": "choice", "options": [2, 3, 5, 7, 11, 13]},
                "ma":   {"type": "randint", "min": 3, "max": 15},
                "m":    {"type": "computed", "expr": "2 * {ma}"},
                "nhalf": {"type": "randint", "min": 2, "max": 10},
                "n":    {"type": "computed", "expr": "2 * {nhalf} + 1"},
            },
            "options": [
                {"id": "Da", "text": "Da",  "is_correct": False},
                {"id": "Nu", "text": "Nu",  "is_correct": True},
            ],
        },
    },
    {
        "name": "Cât de puteri: a^m : a^n cu m - n par (Da)",
        "category": "perfect_square_identify",
        "difficulty": "medium",
        "exercise_type": "multiple_choice",
        "template": {
            "title": "Cât de puteri: a^m : a^n cu m - n par (Da)",
            "type": "multiple_choice",
            "question": "Este numărul ${a}^{{{m}}} : {a}^{{{n}}}$ un pătrat perfect?",
            "params": {
                "a":    {"type": "randint", "min": 2, "max": 15},
                "n":    {"type": "randint", "min": 5, "max": 15},
                "diff": {"type": "randint", "min": 2, "max": 10},
                "m":    {"type": "computed", "expr": "{n} + 2 * {diff}"},
            },
            "options": [
                {"id": "Da", "text": "Da",  "is_correct": True},
                {"id": "Nu", "text": "Nu",  "is_correct": False},
            ],
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Last-digit shortcut on compound expressions
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Sumă de puteri cu ultima cifră 2, 3, 7 sau 8 (Nu)",
        "category": "perfect_square_identify",
        "difficulty": "hard",
        "exercise_type": "multiple_choice",
        "template": {
            "title": "Sumă de puteri cu ultima cifră 2, 3, 7 sau 8 (Nu)",
            "type": "multiple_choice",
            "question": "Este numărul ${a}^{{{m}}} + {b}^{{{n}}}$ un pătrat perfect?",
            "params": {
                # Force u(a^m) = 4 via base ending in 2 with even exponent,
                # u(b^n) = 9 via base ending in 3 with even exponent.
                # 4 + 9 = 13 → last digit 3 → NOT a perfect square.
                "a_tens": {"type": "randint", "min": 1, "max": 9},
                "a":      {"type": "computed", "expr": "{a_tens} * 10 + 2"},
                "b_tens": {"type": "randint", "min": 1, "max": 9},
                "b":      {"type": "computed", "expr": "{b_tens} * 10 + 3"},
                # Even exponent ≡ 2 mod 4 for both → u(a^m) = 4, u(b^n) = 9
                "mk":     {"type": "randint", "min": 50, "max": 500},
                "m":      {"type": "computed", "expr": "4 * {mk} + 2"},
                "nk":     {"type": "randint", "min": 50, "max": 500},
                "n":      {"type": "computed", "expr": "4 * {nk} + 2"},
            },
            "options": [
                {"id": "Da", "text": "Da",  "is_correct": False},
                {"id": "Nu", "text": "Nu",  "is_correct": True},
            ],
        },
    },
    {
        "name": "Produs de puteri cu toți exponenții pari (Da)",
        "category": "perfect_square_identify",
        "difficulty": "hard",
        "exercise_type": "multiple_choice",
        "template": {
            "title": "Produs de puteri cu toți exponenții pari (Da)",
            "type": "multiple_choice",
            "question": "Este numărul ${a}^{{{m}}} \\cdot {b}^{{{n}}} \\cdot {c}^{{{p}}}$ un pătrat perfect?",
            "params": {
                "a":  {"type": "randint", "min": 2, "max": 10},
                "b":  {"type": "randint", "min": 2, "max": 10},
                "c":  {"type": "randint", "min": 2, "max": 10},
                "mk": {"type": "randint", "min": 3, "max": 12},
                "nk": {"type": "randint", "min": 3, "max": 12},
                "pk": {"type": "randint", "min": 3, "max": 12},
                "m":  {"type": "computed", "expr": "2 * {mk}"},
                "n":  {"type": "computed", "expr": "2 * {nk}"},
                "p":  {"type": "computed", "expr": "2 * {pk}"},
            },
            "options": [
                {"id": "Da", "text": "Da",  "is_correct": True},
                {"id": "Nu", "text": "Nu",  "is_correct": False},
            ],
        },
    },
    {
        "name": "Sumă de două puteri ale lui 2 (Nu — ultima cifră)",
        "category": "perfect_square_identify",
        "difficulty": "hard",
        "exercise_type": "multiple_choice",
        "template": {
            "title": "Sumă de două puteri ale lui 2 (Nu — ultima cifră)",
            "type": "multiple_choice",
            "question": "Este numărul $2^{{{m}}} + 2^{{{n}}}$ un pătrat perfect?",
            "params": {
                # Pick m, n so that 2^m + 2^n ends in 2, 3, 7, or 8.
                # 2^m cycle of last digit (m >= 1): 2, 4, 8, 6, 2, 4, 8, 6, ...
                # We want m ≡ 1 mod 4 (→ 2) and n ≡ 2 mod 4 (→ 4), so sum ends in 6
                # ... hmm that's NOT excluded. Let me try m ≡ 1 mod 4 (→ 2) and
                # n ≡ 3 mod 4 (→ 8) → last digit 10 → 0 (ambiguous: 0 is allowed).
                # Safer: m ≡ 2 mod 4 (→ 4) and n ≡ 3 mod 4 (→ 8) → sum ends in 2 → NOT a square.
                "mk": {"type": "randint", "min": 50, "max": 500},
                "m":  {"type": "computed", "expr": "4 * {mk} + 2"},
                "nk": {"type": "randint", "min": 50, "max": 500},
                "n":  {"type": "computed", "expr": "4 * {nk} + 3"},
            },
            "options": [
                {"id": "Da", "text": "Da",  "is_correct": False},
                {"id": "Nu", "text": "Nu",  "is_correct": True},
            ],
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # Pătrate perfecte consecutive — bracketing a non-square (folded into C3)
    #
    # Same conceptual skill as identification ("where does this number sit
    # relative to perfect squares?") — yes/no plus the locator question.
    #
    # All three templates use multi_fill_blank with two fields k and k+1, so
    # students must produce both bracketing roots and prove they understand
    # the spacing of perfect squares on the number line.
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Pătrate perfecte consecutive — număr de 2 cifre",
        "category": "perfect_square_identify",
        "difficulty": "easy",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Pătrate perfecte consecutive — număr de 2 cifre",
            "type": "multi_fill_blank",
            "display_mode": "inline_between",
            "question": "Între ce două pătrate perfecte consecutive se află numărul ${n}$?",
            "params": {
                # k in [3, 8] gives k^2 in [9, 64], (k+1)^2 in [16, 81].
                # Strict-between range has size 2k, so offset in [1, 2k] is safe.
                "k":      {"type": "randint", "min": 3, "max": 8},
                "k1":     {"type": "computed", "expr": "{k} + 1"},
                "offset": {"type": "randint", "min": 1, "max": "2 * {k}"},
                "n":      {"type": "computed", "expr": "{k} * {k} + {offset}"},
                "k_sq":   {"type": "computed", "expr": "{k} * {k}"},
                "k1_sq":  {"type": "computed", "expr": "{k1} * {k1}"},
            },
            "fields": [
                {"key": "lo", "label": "",  "answer_expr": "{k_sq}"},
                {"key": "hi", "label": "",  "answer_expr": "{k1_sq}"},
            ],
            "between_value": "{n}",
            "answer_input": "number",
            "hint": "Calculați pătratele primelor numere naturale: $1^2 = 1$, $2^2 = 4$, $3^2 = 9$, $4^2 = 16$, $5^2 = 25$, $\\ldots$ — și găsiți între care două pătrate se află ${n}$.",
        },
    },
    {
        "name": "Pătrate perfecte consecutive — număr de 3 cifre",
        "category": "perfect_square_identify",
        "difficulty": "medium",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Pătrate perfecte consecutive — număr de 3 cifre",
            "type": "multi_fill_blank",
            "display_mode": "inline_between",
            "question": "Între ce două pătrate perfecte consecutive se află numărul ${n}$?",
            "params": {
                # k in [10, 31] gives k^2 in [100, 961], (k+1)^2 in [121, 1024].
                # All n stay 3-digit. Strict-between range size = 2k.
                "k":      {"type": "randint", "min": 10, "max": 31},
                "k1":     {"type": "computed", "expr": "{k} + 1"},
                "offset": {"type": "randint", "min": 1, "max": "2 * {k}"},
                "n":      {"type": "computed", "expr": "{k} * {k} + {offset}"},
                "k_sq":   {"type": "computed", "expr": "{k} * {k}"},
                "k1_sq":  {"type": "computed", "expr": "{k1} * {k1}"},
            },
            "fields": [
                {"key": "lo", "label": "",  "answer_expr": "{k_sq}"},
                {"key": "hi", "label": "",  "answer_expr": "{k1_sq}"},
            ],
            "between_value": "{n}",
            "answer_input": "number",
            "hint": "Estimați rădăcina pătrată a lui ${n}$: e mai mare de $10$ (deoarece $10^2 = 100$) și mai mică de $32$ (deoarece $32^2 = 1024$). Încercați câteva valori până găsiți cele două pătrate care încadrează ${n}$.",
        },
    },
    {
        "name": "Pătrate perfecte consecutive — număr de 4 cifre",
        "category": "perfect_square_identify",
        "difficulty": "hard",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Pătrate perfecte consecutive — număr de 4 cifre",
            "type": "multi_fill_blank",
            "display_mode": "inline_between",
            "question": "Între ce două pătrate perfecte consecutive se află numărul ${n}$?",
            "params": {
                # k in [32, 99] gives k^2 in [1024, 9801], (k+1)^2 up to 10000.
                "k":      {"type": "randint", "min": 32, "max": 99},
                "k1":     {"type": "computed", "expr": "{k} + 1"},
                "offset": {"type": "randint", "min": 1, "max": "2 * {k}"},
                "n":      {"type": "computed", "expr": "{k} * {k} + {offset}"},
                "k_sq":   {"type": "computed", "expr": "{k} * {k}"},
                "k1_sq":  {"type": "computed", "expr": "{k1} * {k1}"},
            },
            "fields": [
                {"key": "lo", "label": "",  "answer_expr": "{k_sq}"},
                {"key": "hi", "label": "",  "answer_expr": "{k1_sq}"},
            ],
            "between_value": "{n}",
            "answer_input": "number",
            "hint": "Numărul ${n}$ are 4 cifre, deci $k$ este între $32$ ($32^2 = 1024$) și $99$ ($99^2 = 9801$). Încercați să estimați direct rădăcina pătrată: dacă ${n} \\approx 5000$, atunci $k \\approx 70$ (deoarece $70^2 = 4900$).",
        },
    },
]