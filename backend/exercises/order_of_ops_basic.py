"""
Exercise data: order_of_ops_basic
Topic 1.10 — Ordinea efectuării operațiilor

Category: order_of_ops_basic
Label (RO): Ordinea operațiilor — fără paranteze

Tiers:
  Easy   — 2-3 terms, at most one power. Students must know:
             powers first, then × and :, then + and −
             left-to-right for same-precedence ops
  Medium — 4-5 terms with multiple powers and mixed ops.
           Tests that students don't skip precedence levels.
  Hard   — Long expressions (5-6 terms) with subtle precedence.
           Multiple powers, multiple multiplications, all flattened.

Design notes:
  - NO parentheses in any template. That's reserved for categories 2 and 3.
  - All intermediate and final results are non-negative naturals (Grade 5
    constraint). Subtraction templates build via `a - b` where `a ≥ b` by
    construction.
  - Each template has an `ans` computed param that mirrors Python's eval
    of the expression — so the answer is always exactly what `eval(question)`
    would produce if Python respected operator precedence (which it does).

Usage:
    python manage.py load_exercises exercises.order_of_ops_basic
    python manage.py load_exercises exercises.order_of_ops_basic --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 10,  # "Ordinea operațiilor"
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — 2-3 terms, at most one power
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "a^n + b",
        "category": "order_of_ops_basic",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a^n + b",
            "type": "fill_blank",
            "question": "Calculați:  ${a}^{{{n}}} + {b}$",
            "params": {
                "a":   {"type": "randint", "min": 2, "max": 9},
                "n":   {"type": "randint", "min": 2, "max": 4},
                "b":   {"type": "randint", "min": 5, "max": 50},
                "ans": {"type": "computed", "expr": "{a} ** {n} + {b}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Puterea se calculează înaintea adunării. Calculați mai întâi ${a}^{{{n}}}$, apoi adunați ${b}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "a · b + c",
        "category": "order_of_ops_basic",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a · b + c",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot {b} + {c}$",
            "params": {
                "a":   {"type": "randint", "min": 3, "max": 15},
                "b":   {"type": "randint", "min": 3, "max": 15},
                "c":   {"type": "randint", "min": 10, "max": 100},
                "ans": {"type": "computed", "expr": "{a} * {b} + {c}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Înmulțirea se efectuează înaintea adunării. Calculați mai întâi ${a} \\cdot {b}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "a + b · c (inverse order)",
        "category": "order_of_ops_basic",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a + b · c",
            "type": "fill_blank",
            "question": "Calculați:  ${a} + {b} \\cdot {c}$",
            "params": {
                "a":   {"type": "randint", "min": 5, "max": 50},
                "b":   {"type": "randint", "min": 3, "max": 15},
                "c":   {"type": "randint", "min": 3, "max": 15},
                "ans": {"type": "computed", "expr": "{a} + {b} * {c}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Înmulțirea se efectuează înaintea adunării, chiar dacă apare după. Calculați mai întâi ${b} \\cdot {c}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "k · a^n + b",
        "category": "order_of_ops_basic",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "k · a^n + b",
            "type": "fill_blank",
            "question": "Calculați:  ${k} \\cdot {a}^{{{n}}} + {b}$",
            "params": {
                "k":   {"type": "randint", "min": 2, "max": 9},
                "a":   {"type": "randint", "min": 2, "max": 6},
                "n":   {"type": "randint", "min": 2, "max": 3},
                "b":   {"type": "randint", "min": 5, "max": 50},
                "ans": {"type": "computed", "expr": "{k} * {a} ** {n} + {b}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Ordinea: mai întâi puterea ${a}^{{{n}}}$, apoi înmulțirea cu ${k}$, apoi adunarea cu ${b}$.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — 4-5 terms, multiple powers and mixed ops
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "a + b · c − d",
        "category": "order_of_ops_basic",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a + b · c − d",
            "type": "fill_blank",
            "question": "Calculați:  ${a} + {b} \\cdot {c} - {d}$",
            "params": {
                # Min a + b*c = 20 + 5*5 = 45 > max d = 40 → always non-negative.
                "a":   {"type": "randint", "min": 20, "max": 100},
                "b":   {"type": "randint", "min": 5, "max": 15},
                "c":   {"type": "randint", "min": 5, "max": 15},
                "d":   {"type": "randint", "min": 5, "max": 40},
                "ans": {"type": "computed", "expr": "{a} + {b} * {c} - {d}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Înmulțirea ${b} \\cdot {c}$ se efectuează întâi, apoi adunarea și scăderea de la stânga la dreapta.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "a · b + c : d",
        "category": "order_of_ops_basic",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a · b + c : d",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot {b} + {c} : {d}$",
            "params": {
                # Ensure c is divisible by d for exact division.
                "a":   {"type": "randint", "min": 3, "max": 15},
                "b":   {"type": "randint", "min": 3, "max": 15},
                "d":   {"type": "randint", "min": 3, "max": 12},
                "q":   {"type": "randint", "min": 5, "max": 30},
                "c":   {"type": "computed", "expr": "{d} * {q}"},
                "ans": {"type": "computed", "expr": "{a} * {b} + {q}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Înmulțirea și împărțirea se efectuează înaintea adunării. Calculați ${a} \\cdot {b}$ și ${c} : {d}$, apoi adunați rezultatele.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "a^m · b − c^n",
        "category": "order_of_ops_basic",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a^m · b − c^n",
            "type": "fill_blank",
            "question": "Calculați:  ${a}^{{{m}}} \\cdot {b} - {c}^{{{n}}}$",
            "params": {
                # Min a^m*b = 4^2*5 = 80 > max c^n = 3^3 = 27 → always positive.
                "a":   {"type": "randint", "min": 4, "max": 6},
                "m":   {"type": "fixed", "value": 2},
                "b":   {"type": "randint", "min": 5, "max": 15},
                "c":   {"type": "randint", "min": 2, "max": 3},
                "n":   {"type": "randint", "min": 2, "max": 3},
                "ans": {"type": "computed", "expr": "{a} ** {m} * {b} - {c} ** {n}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Calculați puterile întâi: ${a}^{{{m}}}$ și ${c}^{{{n}}}$. Apoi înmulțirea. Apoi scăderea.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "a · b + c · d − e",
        "category": "order_of_ops_basic",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a · b + c · d − e",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot {b} + {c} \\cdot {d} - {e}$",
            "params": {
                # Lower bound on products (min a*b = 5*5 = 25, so 2 products
                # give min 50). e capped at 40 → sum - e >= 10.
                "a":   {"type": "randint", "min": 5, "max": 15},
                "b":   {"type": "randint", "min": 5, "max": 15},
                "c":   {"type": "randint", "min": 5, "max": 15},
                "d":   {"type": "randint", "min": 5, "max": 15},
                "e":   {"type": "randint", "min": 10, "max": 40},
                "ans": {"type": "computed", "expr": "{a} * {b} + {c} * {d} - {e}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Ambele înmulțiri se efectuează întâi, apoi adunarea și scăderea de la stânga la dreapta.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Long flat expressions with multiple powers and ops
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "a · b − c : d + e · f",
        "category": "order_of_ops_basic",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a · b − c : d + e · f",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot {b} - {c} : {d} + {e} \\cdot {f}$",
            "params": {
                # Ensure a*b >= c/d (product term dominates) and exact division.
                "a":   {"type": "randint", "min": 10, "max": 25},
                "b":   {"type": "randint", "min": 10, "max": 25},
                "d":   {"type": "randint", "min": 3, "max": 12},
                "q":   {"type": "randint", "min": 5, "max": 30},
                "c":   {"type": "computed", "expr": "{d} * {q}"},
                "e":   {"type": "randint", "min": 3, "max": 15},
                "f":   {"type": "randint", "min": 3, "max": 15},
                "ans": {"type": "computed", "expr": "{a} * {b} - {q} + {e} * {f}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Toate înmulțirile și împărțirile se efectuează înaintea adunărilor și scăderilor. Calculați ${a} \\cdot {b}$, ${c} : {d}$, ${e} \\cdot {f}$, apoi combinați.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "k · a^n + b^m · c − d",
        "category": "order_of_ops_basic",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "k · a^n + b^m · c − d",
            "type": "fill_blank",
            "question": "Calculați:  ${k} \\cdot {a}^{{{n}}} + {b}^{{{m}}} \\cdot {c} - {d}$",
            "params": {
                # Min: k=2, a^n=4 (2^2), b^m=4, c=3, d=60.
                # Worst case k*a^n + b^m*c = 2*4 + 4*3 = 20 < 60.
                # Force n >= 3 so a^n >= 8, and c >= 5 so b^m*c >= 20.
                # Then min sum = 2*8 + 4*5 = 36, max d = 30 → always positive.
                "k":   {"type": "randint", "min": 2, "max": 6},
                "a":   {"type": "randint", "min": 2, "max": 5},
                "n":   {"type": "fixed", "value": 3},
                "b":   {"type": "randint", "min": 2, "max": 4},
                "m":   {"type": "fixed", "value": 2},
                "c":   {"type": "randint", "min": 5, "max": 10},
                "d":   {"type": "randint", "min": 10, "max": 30},
                "ans": {"type": "computed", "expr": "{k} * {a} ** {n} + {b} ** {m} * {c} - {d}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Ordinea: mai întâi puterile (${a}^{{{n}}}$ și ${b}^{{{m}}}$), apoi înmulțirile, apoi adunarea și scăderea.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "a^n · b + c · d^m − e : f",
        "category": "order_of_ops_basic",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a^n · b + c · d^m − e : f",
            "type": "fill_blank",
            "question": "Calculați:  ${a}^{{{n}}} \\cdot {b} + {c} \\cdot {d}^{{{m}}} - {e} : {f}$",
            "params": {
                "a":   {"type": "randint", "min": 2, "max": 4},
                "n":   {"type": "fixed", "value": 2},
                "b":   {"type": "randint", "min": 3, "max": 10},
                "c":   {"type": "randint", "min": 3, "max": 10},
                "d":   {"type": "randint", "min": 2, "max": 4},
                "m":   {"type": "fixed", "value": 2},
                "f":   {"type": "randint", "min": 3, "max": 10},
                "q":   {"type": "randint", "min": 3, "max": 15},
                "e":   {"type": "computed", "expr": "{f} * {q}"},
                "ans": {"type": "computed", "expr": "{a} ** {n} * {b} + {c} * {d} ** {m} - {q}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Ordinea completă: puteri → înmulțiri și împărțiri → adunări și scăderi. Fiecare nivel se face înainte de trecerea la următorul.",
            "placeholder": "= ?",
        },
    },
]
