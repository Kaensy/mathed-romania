"""
Exercise data: power_compute
Topic 1.8 — Puterea cu exponent natural (sub-lesson A: definiție și reguli)

Category: power_compute
Label (RO): Calcul cu puteri

Tiers:
  Easy   — Single power value, simple two-term sums, a^0 convention
  Medium — Three-term mixed ops, 0^n / 1^n / a^0 conventions combined,
           parenthesized base (a+b)^n, multiplier + power k·a^n + b^m
  Hard   — Four-term mixed expressions, (b-c)^m trick where b-c=1 collapses
           to 1, multiplier-with-power minus a smaller power

Pedagogical focus: students evaluate each power individually, then apply
operation order. This is distinct from power_rules_simplify (A3) where
students use rules to collapse to a single power without computing values.

All templates ensure a non-negative natural-number answer — Grade 5
students work only with natural numbers at this point in the curriculum.

Usage:
    python manage.py load_exercises exercises.power_compute
    python manage.py load_exercises exercises.power_compute --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 8,
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Single / two-term, convention reinforcement
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Calcul: a^n",
        "category": "power_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Calcul: a^n",
            "type": "fill_blank",
            "question": "Calculați:  ${a}^{{{n}}}$",
            "params": {
                "a":   {"type": "randint", "min": 2, "max": 9},
                "n":   {"type": "randint", "min": 2, "max": 4},
                "ans": {"type": "computed", "expr": "{a} ** {n}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "$a^n$ înseamnă ${a}$ înmulțit cu el însuși de ${n}$ ori.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Calcul: a^n + b^m",
        "category": "power_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Calcul: a^n + b^m",
            "type": "fill_blank",
            "question": "Calculați:  ${a}^{{{n}}} + {b}^{{{m}}}$",
            "params": {
                "a":   {"type": "randint", "min": 2, "max": 9},
                "n":   {"type": "randint", "min": 2, "max": 4},
                "b":   {"type": "randint", "min": 2, "max": 9},
                "m":   {"type": "randint", "min": 2, "max": 4},
                "ans": {"type": "computed", "expr": "{a} ** {n} + {b} ** {m}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Calculați mai întâi ${a}^{{{n}}}$ și ${b}^{{{m}}}$, apoi adunați.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Convenție: a^0 + b^n",
        "category": "power_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Convenție: a^0 + b^n",
            "type": "fill_blank",
            "question": "Calculați:  ${a}^0 + {b}^{{{n}}}$",
            "params": {
                "a":   {"type": "randint", "min": 2, "max": 99},
                "b":   {"type": "randint", "min": 2, "max": 9},
                "n":   {"type": "randint", "min": 2, "max": 4},
                "ans": {"type": "computed", "expr": "1 + {b} ** {n}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Prin convenție, orice număr nenul ridicat la puterea $0$ este egal cu $1$. Deci ${a}^0 = 1$.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Three-term, conventions combined, parens, multiplier
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Trei termeni: a^n + b^m - c^p",
        "category": "power_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Trei termeni: a^n + b^m - c^p",
            "type": "fill_blank",
            "question": "Calculați:  ${a}^{{{n}}} + {b}^{{{m}}} - {c}^{{{p}}}$",
            "params": {
                # Bounds chosen to guarantee non-negative result:
                # min a^n + b^m = 9 + 4 = 13, max c^p = 9.
                "a":   {"type": "randint", "min": 3, "max": 7},
                "n":   {"type": "randint", "min": 2, "max": 4},
                "b":   {"type": "randint", "min": 2, "max": 6},
                "m":   {"type": "randint", "min": 2, "max": 3},
                "c":   {"type": "randint", "min": 2, "max": 3},
                "p":   {"type": "fixed", "value": 2},
                "ans": {"type": "computed", "expr": "{a} ** {n} + {b} ** {m} - {c} ** {p}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Calculați fiecare putere, apoi efectuați adunarea și scăderea de la stânga la dreapta.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Convenții combinate: 1^p + 0^q + a^0 + b^n",
        "category": "power_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Convenții combinate: 1^p + 0^q + a^0 + b^n",
            "type": "fill_blank",
            "question": "Calculați:  $1^{{{p}}} + 0^{{{q}}} + {a}^0 + {b}^{{{n}}}$",
            "params": {
                "p":   {"type": "choice", "options": [31, 100, 2011, 2024]},
                "q":   {"type": "choice", "options": [3, 200, 2011]},
                "a":   {"type": "randint", "min": 2, "max": 50},
                "b":   {"type": "randint", "min": 2, "max": 6},
                "n":   {"type": "randint", "min": 2, "max": 4},
                # 1^anything = 1, 0^(>=1) = 0, a^0 = 1 (a != 0)
                "ans": {"type": "computed", "expr": "2 + {b} ** {n}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "$1^p = 1$ oricât de mare ar fi $p$. $0^q = 0$ pentru $q \\geq 1$. ${a}^0 = 1$ pentru $a \\neq 0$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Bază sub paranteză: (a+b)^n",
        "category": "power_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Bază sub paranteză: (a+b)^n",
            "type": "fill_blank",
            "question": "Calculați:  $({a} + {b})^{{{n}}}$",
            "params": {
                "a":   {"type": "randint", "min": 1, "max": 5},
                "b":   {"type": "randint", "min": 1, "max": 5},
                "n":   {"type": "randint", "min": 2, "max": 4},
                "ans": {"type": "computed", "expr": "({a} + {b}) ** {n}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Calculați mai întâi paranteza: ${a} + {b}$. Apoi ridicați rezultatul la puterea ${n}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Factor cu putere: k · a^n + b^m",
        "category": "power_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Factor cu putere: k · a^n + b^m",
            "type": "fill_blank",
            "question": "Calculați:  ${k} \\cdot {a}^{{{n}}} + {b}^{{{m}}}$",
            "params": {
                "k":   {"type": "randint", "min": 2, "max": 9},
                "a":   {"type": "randint", "min": 2, "max": 6},
                "n":   {"type": "randint", "min": 2, "max": 4},
                "b":   {"type": "randint", "min": 2, "max": 6},
                "m":   {"type": "randint", "min": 2, "max": 4},
                "ans": {"type": "computed", "expr": "{k} * {a} ** {n} + {b} ** {m}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Puterea se calculează înaintea înmulțirii. Calculați ${a}^{{{n}}}$ și ${b}^{{{m}}}$, apoi efectuați înmulțirea și adunarea.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Four-term mixed, 1^m collapse trick, multiplier minus power
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Patru termeni: a^n + b^m - c^p + d^q",
        "category": "power_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Patru termeni: a^n + b^m - c^p + d^q",
            "type": "fill_blank",
            "question": "Calculați:  ${a}^{{{n}}} + {b}^{{{m}}} - {c}^{{{p}}} + {d}^{{{q}}}$",
            "params": {
                # Bounds ensure non-negative: min a^n + b^m + d^q = 9+9+4 = 22 > max c^p = 9.
                "a":   {"type": "randint", "min": 3, "max": 9},
                "n":   {"type": "randint", "min": 2, "max": 4},
                "b":   {"type": "randint", "min": 3, "max": 9},
                "m":   {"type": "randint", "min": 2, "max": 4},
                "c":   {"type": "randint", "min": 2, "max": 3},
                "p":   {"type": "fixed", "value": 2},
                "d":   {"type": "randint", "min": 2, "max": 7},
                "q":   {"type": "randint", "min": 2, "max": 3},
                "ans": {"type": "computed", "expr": "{a} ** {n} + {b} ** {m} - {c} ** {p} + {d} ** {q}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Calculați fiecare putere separat, apoi efectuați adunările și scăderile de la stânga la dreapta.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Convenție 1^m: a^2 - (b - c)^m cu b - c = 1",
        "category": "power_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Convenție 1^m: a^2 - (b - c)^m cu b - c = 1",
            "type": "fill_blank",
            "question": "Calculați:  ${a}^2 - ({b} - {c})^{{{m}}}$",
            "params": {
                "a":   {"type": "randint", "min": 3, "max": 15},
                "c":   {"type": "randint", "min": 1, "max": 10},
                "b":   {"type": "computed", "expr": "{c} + 1"},
                "m":   {"type": "choice", "options": [5, 10, 100, 2011, 2024]},
                "ans": {"type": "computed", "expr": "{a} ** 2 - 1"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Calculați paranteza: ${b} - {c} = 1$. Apoi $1^m = 1$ pentru orice $m$, deci expresia devine ${a}^2 - 1$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Putere cu factor minus putere: k · a^n - b^m",
        "category": "power_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Putere cu factor minus putere: k · a^n - b^m",
            "type": "fill_blank",
            "question": "Calculați:  ${k} \\cdot {a}^{{{n}}} - {b}^{{{m}}}$",
            "params": {
                # Ensure k * a^n >= b^m. With a >= 3, n >= 2, k >= 3:
                # min k * a^n = 3 * 9 = 27; max b^m with b <= 3, m <= 3 = 27.
                "k":   {"type": "randint", "min": 3, "max": 9},
                "a":   {"type": "randint", "min": 3, "max": 6},
                "n":   {"type": "randint", "min": 2, "max": 3},
                "b":   {"type": "randint", "min": 2, "max": 3},
                "m":   {"type": "randint", "min": 2, "max": 3},
                "ans": {"type": "computed", "expr": "{k} * {a} ** {n} - {b} ** {m}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Ordinea operațiilor: mai întâi puterile, apoi înmulțirea, apoi scăderea.",
            "placeholder": "= ?",
        },
    },
]
