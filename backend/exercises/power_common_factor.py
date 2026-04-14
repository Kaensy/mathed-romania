"""
Exercise data: power_common_factor
Topic 1.8 — Puterea cu exponent natural (sub-lesson A: definiție și reguli)

Category: power_common_factor
Label (RO): Factor comun cu puteri

Tiers:
  Easy   — Two-term sum with common base: a^(n+k) + a^n = a^n · (a^k + 1)
           Student gives the numeric multiplier in front of a^n.
  Medium — Three-term expressions a^(n+p) ± a^(n+q) ± a^n where student
           factors out a^n and provides the numeric scalar.
  Hard   — Compound: factor out a common power, then rewrite as a cleaner
           power (e.g., 2^29 + 2^27 - 2^26 = 9 · 4^13).

Design notes:
  - Answer format is numeric (the scalar k in "k · a^m"). This avoids the
    ambiguity of symbolic factored forms ("which factorization is 'the'
    answer?") — students compute the simplified coefficient.
  - For Hard tier we use multi_fill_blank so students must surface BOTH
    the scalar AND the rebased power, proving they can do the full move.
  - All numeric bounds chosen so the simplified scalar stays a small,
    recognizable number (often yielding clean forms like 9, 7, 3, 5).

Usage:
    python manage.py load_exercises exercises.power_common_factor
    python manage.py load_exercises exercises.power_common_factor --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 8,
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Two-term factor-out
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Factor comun: a^(n+k) + a^n",
        "category": "power_common_factor",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Factor comun: a^(n+k) + a^n",
            "type": "fill_blank",
            "question": "Scoateți factorul comun ${a}^{{{n}}}$ și aflați numărul natural $x$ astfel încât:  ${a}^{{{m}}} + {a}^{{{n}}} = x \\cdot {a}^{{{n}}}$",
            "params": {
                "a":     {"type": "randint", "min": 2, "max": 7},
                "n":     {"type": "randint", "min": 10, "max": 20},
                "k":     {"type": "randint", "min": 1, "max": 3},
                "m":     {"type": "computed", "expr": "{n} + {k}"},
                "scale": {"type": "computed", "expr": "{a} ** {k} + 1"},
            },
            "answer_expr": "{scale}",
            "answer_input": "number",
            "hint": "Scoateți ${a}^{{{n}}}$ factor comun: ${a}^{{{m}}} + {a}^{{{n}}} = {a}^{{{n}}} \\cdot ({a}^{{{k}}} + 1)$. Calculați paranteza.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Factor comun cu scădere: a^(n+k) - a^n",
        "category": "power_common_factor",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Factor comun cu scădere: a^(n+k) - a^n",
            "type": "fill_blank",
            "question": "Scoateți factorul comun ${a}^{{{n}}}$ și aflați numărul natural $x$ astfel încât:  ${a}^{{{m}}} - {a}^{{{n}}} = x \\cdot {a}^{{{n}}}$",
            "params": {
                "a":     {"type": "randint", "min": 2, "max": 7},
                "n":     {"type": "randint", "min": 10, "max": 20},
                "k":     {"type": "randint", "min": 1, "max": 3},
                "m":     {"type": "computed", "expr": "{n} + {k}"},
                "scale": {"type": "computed", "expr": "{a} ** {k} - 1"},
            },
            "answer_expr": "{scale}",
            "answer_input": "number",
            "hint": "Scoateți ${a}^{{{n}}}$ factor comun: ${a}^{{{m}}} - {a}^{{{n}}} = {a}^{{{n}}} \\cdot ({a}^{{{k}}} - 1)$.",
            "placeholder": "x = ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Three-term factor-out
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Factor comun: a^(n+2) + a^(n+1) + a^n",
        "category": "power_common_factor",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Factor comun: a^(n+2) + a^(n+1) + a^n",
            "type": "fill_blank",
            "question": "Scoateți factorul comun ${a}^{{{n}}}$ și aflați numărul natural $x$ astfel încât:  ${a}^{{{n2}}} + {a}^{{{n1}}} + {a}^{{{n}}} = x \\cdot {a}^{{{n}}}$",
            "params": {
                "a":     {"type": "randint", "min": 2, "max": 7},
                "n":     {"type": "randint", "min": 10, "max": 25},
                "n1":    {"type": "computed", "expr": "{n} + 1"},
                "n2":    {"type": "computed", "expr": "{n} + 2"},
                "scale": {"type": "computed", "expr": "{a} ** 2 + {a} + 1"},
            },
            "answer_expr": "{scale}",
            "answer_input": "number",
            "hint": "Scoateți ${a}^{{{n}}}$: ${a}^{{{n2}}} + {a}^{{{n1}}} + {a}^{{{n}}} = {a}^{{{n}}} \\cdot ({a}^2 + {a} + 1)$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Factor comun cu semne mixte: a^(n+p) + a^(n+q) - a^n",
        "category": "power_common_factor",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Factor comun cu semne mixte: a^(n+p) + a^(n+q) - a^n",
            "type": "fill_blank",
            "question": "Scoateți factorul comun ${a}^{{{n}}}$ și aflați numărul natural $x$ astfel încât:  ${a}^{{{np}}} + {a}^{{{nq}}} - {a}^{{{n}}} = x \\cdot {a}^{{{n}}}$",
            "params": {
                "a":     {"type": "randint", "min": 2, "max": 5},
                "n":     {"type": "randint", "min": 10, "max": 25},
                "p":     {"type": "randint", "min": 2, "max": 4},
                "q":     {"type": "randint", "min": 1, "max": 2},
                "np":    {"type": "computed", "expr": "{n} + {p}"},
                "nq":    {"type": "computed", "expr": "{n} + {q}"},
                "scale": {"type": "computed", "expr": "{a} ** {p} + {a} ** {q} - 1"},
            },
            "answer_expr": "{scale}",
            "answer_input": "number",
            "hint": "Scoateți ${a}^{{{n}}}$: expresia devine ${a}^{{{n}}} \\cdot ({a}^{{{p}}} + {a}^{{{q}}} - 1)$. Calculați paranteza.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Factor comun cu coeficienți: k·a^m + a^n",
        "category": "power_common_factor",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Factor comun cu coeficienți: k·a^m + a^n",
            "type": "fill_blank",
            "question": "Scoateți factorul comun ${a}^{{{n}}}$ și aflați numărul natural $x$ astfel încât:  ${k} \\cdot {a}^{{{m}}} + {a}^{{{n}}} = x \\cdot {a}^{{{n}}}$",
            "params": {
                "a":     {"type": "randint", "min": 2, "max": 5},
                "n":     {"type": "randint", "min": 10, "max": 25},
                "d":     {"type": "randint", "min": 2, "max": 4},
                "m":     {"type": "computed", "expr": "{n} + {d}"},
                "k":     {"type": "randint", "min": 2, "max": 6},
                "scale": {"type": "computed", "expr": "{k} * {a} ** {d} + 1"},
            },
            "answer_expr": "{scale}",
            "answer_input": "number",
            "hint": "Scoateți ${a}^{{{n}}}$: ${k} \\cdot {a}^{{{m}}} + {a}^{{{n}}} = {a}^{{{n}}} \\cdot ({k} \\cdot {a}^{{{d}}} + 1)$.",
            "placeholder": "x = ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Factor out AND rebase the remaining power
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Factor comun + rebazare: 2^(n+3) + 2^(n+1) - 2^n",
        "category": "power_common_factor",
        "difficulty": "hard",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Factor comun + rebazare: 2^(n+3) + 2^(n+1) - 2^n",
            "type": "multi_fill_blank",
            "question": "Aduceți expresia la forma  $x \\cdot 4^y$, unde $x$ și $y$ sunt numere naturale:  $2^{{{n3}}} + 2^{{{n1}}} - 2^{{{n}}}$",
            "params": {
                # We want the sum to reduce to 9 · 2^n, and we want the
                # remaining 2^n to rebase cleanly to 4^y. So n must be even.
                # n in {14, 16, 18, 20, 22, 24, 26}: y in {7..13}.
                "half":  {"type": "randint", "min": 7, "max": 13},
                "n":     {"type": "computed", "expr": "2 * {half}"},
                "n1":    {"type": "computed", "expr": "{n} + 1"},
                "n3":    {"type": "computed", "expr": "{n} + 3"},
                "x_val": {"type": "fixed", "value": 9},
                # y_val = n / 2 = half
                "y_val": {"type": "computed", "expr": "{half}"},
            },
            "fields": [
                {"key": "x", "label": "x", "answer_expr": "{x_val}"},
                {"key": "y", "label": "y", "answer_expr": "{y_val}"},
            ],
            "answer_input": "number",
            "hint": "Pasul 1: scoateți $2^{{{n}}}$ factor comun. Ce sumă rămâne în paranteză? Pasul 2: rescrieți $2^{{{n}}}$ ca o putere a lui $4$ folosind $2^{{2k}} = 4^k$.",
        },
    },
    {
        "name": "Factor comun + rebazare: 3^(n+2) - 3^(n+1) + 3^n",
        "category": "power_common_factor",
        "difficulty": "hard",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Factor comun + rebazare: 3^(n+2) - 3^(n+1) + 3^n",
            "type": "multi_fill_blank",
            "question": "Aduceți expresia la forma  $x \\cdot 9^y$, unde $x$ și $y$ sunt numere naturale:  $3^{{{n2}}} - 3^{{{n1}}} + 3^{{{n}}}$",
            "params": {
                # 3^(n+2) - 3^(n+1) + 3^n = 3^n · (9 - 3 + 1) = 7 · 3^n.
                # n must be even for clean 9^y form.
                "half":  {"type": "randint", "min": 5, "max": 12},
                "n":     {"type": "computed", "expr": "2 * {half}"},
                "n1":    {"type": "computed", "expr": "{n} + 1"},
                "n2":    {"type": "computed", "expr": "{n} + 2"},
                "x_val": {"type": "fixed", "value": 7},
                "y_val": {"type": "computed", "expr": "{half}"},
            },
            "fields": [
                {"key": "x", "label": "x", "answer_expr": "{x_val}"},
                {"key": "y", "label": "y", "answer_expr": "{y_val}"},
            ],
            "answer_input": "number",
            "hint": "Pasul 1: scoateți $3^{{{n}}}$ factor comun. Paranteza: $3^2 - 3 + 1$. Pasul 2: rescrieți $3^{{{n}}}$ ca putere a lui $9$ folosind $3^{{2k}} = 9^k$.",
        },
    },
    {
        "name": "Factor comun + rebazare: 5^(n+1) + 5^n",
        "category": "power_common_factor",
        "difficulty": "hard",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Factor comun + rebazare: 5^(n+1) + 5^n",
            "type": "multi_fill_blank",
            "question": "Aduceți expresia la forma  $x \\cdot 25^y$, unde $x$ și $y$ sunt numere naturale:  $5^{{{n1}}} + 5^{{{n}}}$",
            "params": {
                # 5^(n+1) + 5^n = 5^n · (5 + 1) = 6 · 5^n.
                # For 25^y form we need n even.
                "half":  {"type": "randint", "min": 5, "max": 12},
                "n":     {"type": "computed", "expr": "2 * {half}"},
                "n1":    {"type": "computed", "expr": "{n} + 1"},
                "x_val": {"type": "fixed", "value": 6},
                "y_val": {"type": "computed", "expr": "{half}"},
            },
            "fields": [
                {"key": "x", "label": "x", "answer_expr": "{x_val}"},
                {"key": "y", "label": "y", "answer_expr": "{y_val}"},
            ],
            "answer_input": "number",
            "hint": "Pasul 1: scoateți $5^{{{n}}}$ factor comun — în paranteză rămâne $5 + 1$. Pasul 2: rescrieți $5^{{{n}}}$ ca putere a lui $25$ folosind $5^{{2k}} = 25^k$.",
        },
    },
]
