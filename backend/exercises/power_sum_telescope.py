"""
Exercise data: power_sum_telescope
Topic 1.8 — Puterea cu exponent natural (sub-lesson B: ultima cifră, sume)

Category: power_sum_telescope
Label (RO): Sume de puteri consecutive

Tiers:
  Easy   — Small-n consecutive sums with numeric answer:
             S = 1 + a + a^2 + ... + a^n  for small n (n <= 10)
             Student computes the integer value directly.
  Medium — Large-n sums, symbolic closed-form answer:
             S = 1 + a + a^2 + ... + a^n   →   (a^(n+1) - 1) / (a - 1)
             Student applies multiply-and-subtract, provides the expression.
  Hard   — Variations requiring a normalization step before applying:
             a + a^2 + ... + a^n           (starts from a, not 1)
             1 + 2·a + 2·a^2 + ... + 2·a^n (leading 1, then factor-of-2 tail)
             mixed-base sums that decompose

Design notes:
  - SymPy grades `answer_input: "expression"` symbolically, so we can accept
    `(a^(n+1) - 1) / (a - 1)` or any equivalent simplification (e.g., the
    student could compute and submit the integer).
  - For Easy we keep the sum small (n <= 10) so the student can actually
    compute `1 + a + a^2 + ... + a^n` by hand and check their work.
  - Medium uses n in 2000-ish range — computing numerically is infeasible,
    forcing the student to apply the telescoping technique.
  - For base 2 the denominator is 1, so the formula simplifies to
    `2^(n+1) - 1`. We handle this as its own template for clarity.

Usage:
    python manage.py load_exercises exercises.power_sum_telescope
    python manage.py load_exercises exercises.power_sum_telescope --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 8,
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Small-n, numeric answer
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Sumă mică: 1 + 2 + 2² + ... + 2^n",
        "category": "power_sum_telescope",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Sumă mică: 1 + 2 + 2² + ... + 2^n",
            "type": "fill_blank",
            "question": "Calculați:  $S = 1 + 2 + 2^2 + 2^3 + \\ldots + 2^{{{n}}}$",
            "params": {
                "n":   {"type": "randint", "min": 5, "max": 10},
                "ans": {"type": "computed", "expr": "2 ** ({n} + 1) - 1"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Puteți calcula direct, sau folosiți tehnica: înmulțiți $S$ cu $2$ și scădeți $S$ din $2S$.",
            "placeholder": "S = ?",
        },
    },
    {
        "name": "Sumă mică: 1 + 3 + 3² + ... + 3^n",
        "category": "power_sum_telescope",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Sumă mică: 1 + 3 + 3² + ... + 3^n",
            "type": "fill_blank",
            "question": "Calculați:  $S = 1 + 3 + 3^2 + 3^3 + \\ldots + 3^{{{n}}}$",
            "params": {
                "n":   {"type": "randint", "min": 4, "max": 7},
                "ans": {"type": "computed", "expr": "(3 ** ({n} + 1) - 1) // 2"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Puteți calcula direct, sau folosiți tehnica: înmulțiți $S$ cu $3$, scădeți $S$ din $3S$, apoi împărțiți la $2$.",
            "placeholder": "S = ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Large-n, symbolic answer
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Telescopare: 1 + 2 + 2² + ... + 2^n (n mare)",
        "category": "power_sum_telescope",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Telescopare: 1 + 2 + 2² + ... + 2^n (n mare)",
            "type": "fill_blank",
            "question": "Calculați, scriind rezultatul sub formă de diferență de puteri:  $S = 1 + 2 + 2^2 + 2^3 + \\ldots + 2^{{{n}}}$",
            "params": {
                "n":  {"type": "choice", "options": [100, 500, 1000, 2016, 2024]},
                "n1": {"type": "computed", "expr": "{n} + 1"},
            },
            "answer_expr": "2**{n1} - 1",
            "answer_input": "expression",
            "hint": "Înmulțiți $S$ cu $2$: obțineți $2S = 2 + 2^2 + \\ldots + 2^{{{n1}}}$. Scădeți $S$ din $2S$ — se anulează toți termenii comuni și rămâne $2^{{{n1}}} - 1$.",
            "placeholder": "ex: 2^2025 - 1",
        },
    },
    {
        "name": "Telescopare: 1 + a + a² + ... + a^n (a ≥ 3, n mare)",
        "category": "power_sum_telescope",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Telescopare: 1 + a + a² + ... + a^n (a ≥ 3, n mare)",
            "type": "fill_blank",
            "question": "Calculați:  $S = 1 + {a} + {a}^2 + {a}^3 + \\ldots + {a}^{{{n}}}$",
            "params": {
                "a":   {"type": "choice", "options": [3, 4, 5]},
                "n":   {"type": "choice", "options": [100, 500, 1000, 2018]},
                "n1":  {"type": "computed", "expr": "{n} + 1"},
                "den": {"type": "computed", "expr": "{a} - 1"},
            },
            "answer_expr": "({a}**{n1} - 1) / {den}",
            "answer_input": "expression",
            "hint": "Înmulțiți $S$ cu ${a}$, apoi scădeți $S$ din ${a} \\cdot S$. Obțineți $({a} - 1) \\cdot S = {a}^{{{n1}}} - 1$. Împărțiți la ${den}$.",
            "placeholder": "ex: (3^2019 - 1) / 2",
        },
    },
    {
        "name": "Telescopare cu bază dată: S = 1 + 5 + 5² + ... + 5^n",
        "category": "power_sum_telescope",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Telescopare cu bază dată: S = 1 + 5 + 5² + ... + 5^n",
            "type": "fill_blank",
            "question": "Calculați:  $S = 1 + 5 + 5^2 + 5^3 + \\ldots + 5^{{{n}}}$",
            "params": {
                "n":  {"type": "choice", "options": [2018, 2020, 2024]},
                "n1": {"type": "computed", "expr": "{n} + 1"},
            },
            "answer_expr": "(5**{n1} - 1) / 4",
            "answer_input": "expression",
            "hint": "Înmulțiți $S$ cu $5$: $5S = 5 + 5^2 + \\ldots + 5^{{{n1}}}$. Scădeți $S$ din $5S$ — rămâne $4S = 5^{{{n1}}} - 1$.",
            "placeholder": "ex: (5^2025 - 1) / 4",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Normalization required before applying telescoping
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Fără termen 1: S = a + a² + ... + a^n",
        "category": "power_sum_telescope",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Fără termen 1: S = a + a² + ... + a^n",
            "type": "fill_blank",
            "question": "Calculați:  $S = {a} + {a}^2 + {a}^3 + \\ldots + {a}^{{{n}}}$",
            "params": {
                "a":   {"type": "choice", "options": [2, 3, 5]},
                "n":   {"type": "choice", "options": [1000, 2016, 2024]},
                "n1":  {"type": "computed", "expr": "{n} + 1"},
                "den": {"type": "computed", "expr": "{a} - 1"},
            },
            "answer_expr": "({a}**{n1} - {a}) / {den}",
            "answer_input": "expression",
            "hint": "Observați că suma începe de la ${a}$, nu de la $1$. Puteți scoate factor comun ${a}$: $S = {a} \\cdot (1 + {a} + {a}^2 + \\ldots + {a}^{{{n} - 1}})$, apoi aplicați tehnica. Sau adunați $1$ la $S$, aplicați tehnica, apoi scădeți $1$ la final.",
            "placeholder": "ex: (2^2025 - 2) / 1",
        },
    },
    {
        "name": "Sumă cu pas 2: 2 + 2·3 + 2·3² + ... + 2·3^n",
        "category": "power_sum_telescope",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Sumă cu pas 2: 2 + 2·3 + 2·3² + ... + 2·3^n",
            "type": "fill_blank",
            "question": "Calculați:  $S = 2 + 2 \\cdot 3 + 2 \\cdot 3^2 + 2 \\cdot 3^3 + \\ldots + 2 \\cdot 3^{{{n}}}$",
            "params": {
                "n":  {"type": "choice", "options": [1000, 2016, 2024]},
                "n1": {"type": "computed", "expr": "{n} + 1"},
            },
            "answer_expr": "3**{n1} - 1",
            "answer_input": "expression",
            "hint": "Scoateți factorul comun $2$: $S = 2 \\cdot (1 + 3 + 3^2 + \\ldots + 3^{{{n}}})$. Aplicați tehnica telescopării pe paranteză: rezultatul este $(3^{{{n1}}} - 1) / 2$. Înmulțit cu $2$, obțineți $3^{{{n1}}} - 1$.",
            "placeholder": "ex: 3^2025 - 1",
        },
    },
    {
        "name": "Telescopare prin înmulțire recursivă (formă specială)",
        "category": "power_sum_telescope",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Telescopare prin înmulțire recursivă",
            "type": "fill_blank",
            "question": "Calculați:  $(\\ldots(((2 + 2) \\cdot 2 + 2^3) \\cdot 2 + 2^5) \\cdot 2 + \\ldots + 2^{{{n}}}) \\cdot 2 + 2^{{{n2}}}$",
            "params": {
                # Pattern from Ex 21 textbook: each step doubles and adds next odd power.
                # The result unfolds to 2^(n+3) via a geometric telescoping.
                # For the form in the textbook, with final exponent 2003:
                # n odd, n2 = n + 2; answer = 2^(n+3).
                "half": {"type": "randint", "min": 500, "max": 1012},  # keeps n odd and n <= 2025
                "n":    {"type": "computed", "expr": "2 * {half} + 1"},  # odd
                "n2":   {"type": "computed", "expr": "{n} + 2"},
                "fin":  {"type": "computed", "expr": "{n} + 3"},
            },
            "answer_expr": "2**{fin}",
            "answer_input": "expression",
            "hint": "Urmăriți structura: la fiecare pas, rezultatul parțial se înmulțește cu $2$ și se adaugă următoarea putere impară a lui $2$. Toți termenii se combină telescopic într-o singură putere a lui $2$. Rezultatul final este $2^{{{n} + 3}}$.",
            "placeholder": "ex: 2^2006",
        },
    },
]
