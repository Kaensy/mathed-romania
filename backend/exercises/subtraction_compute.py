"""
Exercise data: subtraction_compute
Topic 1.5 — Scăderea numerelor naturale

Category: subtraction_compute
Label (RO): Calcul cu scăderi

Tiers:
  Easy   — Direct subtraction (2-3 terms), property a−(b−c)
  Medium — Larger numbers, property a−b−c=a−(b+c)
  Hard   — Nested brackets: [], {}

Usage:
    python manage.py load_exercises exercises.subtraction_compute
    python manage.py load_exercises exercises.subtraction_compute --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 5,  # "Scăderea numerelor naturale" (id=6)
}

EXERCISES = [

    # ── EASY ─────────────────────────────────────────────────────────────────

    {
        "name": "Scădere: două numere de 3 cifre",
        "category": "subtraction_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Scădere: două numere de 3 cifre",
            "type": "fill_blank",
            "question": "Calculați:  ${a} - {b}$",
            "params": {
                "b": {"type": "randint", "min": 100, "max": 499},
                "a": {"type": "randint", "min": 500, "max": 999},
            },
            "answer_expr": "{a} - {b}",
            "answer_input": "number",
            "hint": "Scădeți cele două numere.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Scădere: două numere de 4-5 cifre",
        "category": "subtraction_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Scădere: două numere de 4-5 cifre",
            "type": "fill_blank",
            "question": "Calculați:  ${a} - {b}$",
            "params": {
                "b": {"type": "randint", "min": 1000, "max": 49999},
                "a": {"type": "randint", "min": 50000, "max": 99999},
            },
            "answer_expr": "{a} - {b}",
            "answer_input": "number",
            "hint": "Scădeți cele două numere.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Scădere: trei termeni (a − b − c)",
        "category": "subtraction_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Scădere: trei termeni (a − b − c)",
            "type": "fill_blank",
            "question": "Calculați:  ${a} - {b} - {c}$",
            "params": {
                "b": {"type": "randint", "min": 10, "max": 200},
                "c": {"type": "randint", "min": 10, "max": 200},
                "a": {"type": "randint", "min": 500, "max": 2000},
            },
            "answer_expr": "{a} - {b} - {c}",
            "answer_input": "number",
            "hint": "Scădeți pe rând, de la stânga la dreapta: $({a} - {b}) - {c}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Proprietate: a − (b − c)",
        "category": "subtraction_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Proprietate: a − (b − c)",
            "type": "fill_blank",
            "question": "Efectuați:  ${a} - ({b} - {c})$",
            "params": {
                "c": {"type": "randint", "min": 10, "max": 200},
                "b": {"type": "randint", "min": 250, "max": 600},
                "a": {"type": "randint", "min": 700, "max": 2000},
            },
            "answer_expr": "{a} - {b} + {c}",
            "answer_input": "number",
            "hint": "Calculați mai întâi paranteza: ${b} - {c}$, apoi scădeți din ${a}$. Sau: $a - (b - c) = a - b + c$.",
            "placeholder": "= ?",
        },
    },

    # ── MEDIUM ───────────────────────────────────────────────────────────────

    {
        "name": "Scădere: numere mari (5-6 cifre)",
        "category": "subtraction_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Scădere: numere mari (5-6 cifre)",
            "type": "fill_blank",
            "question": "Calculați:  ${a} - {b}$",
            "params": {
                "b": {"type": "randint", "min": 10000, "max": 499999},
                "a": {"type": "randint", "min": 500000, "max": 999999},
            },
            "answer_expr": "{a} - {b}",
            "answer_input": "number",
            "hint": "Scădeți cele două numere. Aveți grijă la împrumut!",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Proprietate: a − b − c = a − (b + c) (mare)",
        "category": "subtraction_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Proprietate: a − b − c = a − (b + c) (mare)",
            "type": "fill_blank",
            "question": "Efectuați:  ${a} - {b} - {c}$",
            "params": {
                "b": {"type": "randint", "min": 100, "max": 5000},
                "c": {"type": "randint", "min": 100, "max": 5000},
                "a": {"type": "randint", "min": 10000, "max": 50000},
            },
            "answer_expr": "{a} - {b} - {c}",
            "answer_input": "number",
            "hint": "Puteți calcula $({a} - {b}) - {c}$ sau ${a} - ({b} + {c})$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Expresie cu paranteze: a − (b − c) mare",
        "category": "subtraction_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Expresie cu paranteze: a − (b − c) mare",
            "type": "fill_blank",
            "question": "Efectuați:  ${a} - ({b} - {c})$",
            "params": {
                "c": {"type": "randint", "min": 100, "max": 3000},
                "b": {"type": "randint", "min": 3500, "max": 8000},
                "a": {"type": "randint", "min": 8500, "max": 20000},
            },
            "answer_expr": "{a} - {b} + {c}",
            "answer_input": "number",
            "hint": "Folosiți proprietatea: $a - (b - c) = a - b + c = {a} - {b} + {c}$.",
            "placeholder": "= ?",
        },
    },

    # ── HARD ──────────────────────────────────────────────────────────────────

    {
        "name": "Paranteze pătrate: a − [b − (c − d)]",
        "category": "subtraction_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Paranteze pătrate: a − [b − (c − d)]",
            "type": "fill_blank",
            "question": "Efectuați:  ${a} - [{b} - ({c} - {d})]$",
            "params": {
                "d": {"type": "randint", "min": 10, "max": 100},
                "c": {"type": "randint", "min": 200, "max": 500},
                "b": {"type": "randint", "min": 600, "max": 1500},
                "a": {"type": "randint", "min": 2000, "max": 5000},
            },
            "answer_expr": "{a} - {b} + {c} - {d}",
            "answer_input": "number",
            "hint": "Din interior spre exterior: mai întâi $({c} - {d})$, apoi $[{b} - \\ldots]$, apoi scădeți din ${a}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Acolade: a − {b − [c − (d − e)]}",
        "category": "subtraction_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Acolade: a − {b − [c − (d − e)]}",
            "type": "fill_blank",
            "question": "Efectuați:  ${a} - \\{{{b} - [{c} - ({d} - {e})]\\}}$",
            "params": {
                "e": {"type": "randint", "min": 1, "max": 50},
                "d": {"type": "randint", "min": 100, "max": 300},
                "c": {"type": "randint", "min": 400, "max": 800},
                "b": {"type": "randint", "min": 1000, "max": 3000},
                "a": {"type": "randint", "min": 5000, "max": 15000},
            },
            "answer_expr": "{a} - {b} + {c} - {d} + {e}",
            "answer_input": "number",
            "hint": "Desfaceți din interior spre exterior. Fiecare minus în fața unei paranteze schimbă semnele din interior!",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Expresie complexă: a − (b − c) − (d − e)",
        "category": "subtraction_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Expresie complexă: a − (b − c) − (d − e)",
            "type": "fill_blank",
            "question": "Efectuați:  ${a} - ({b} - {c}) - ({d} - {e})$",
            "params": {
                "c": {"type": "randint", "min": 50, "max": 300},
                "b": {"type": "randint", "min": 400, "max": 800},
                "e": {"type": "randint", "min": 50, "max": 300},
                "d": {"type": "randint", "min": 400, "max": 800},
                "a": {"type": "randint", "min": 5000, "max": 12000},
            },
            "answer_expr": "{a} - {b} + {c} - {d} + {e}",
            "answer_input": "number",
            "hint": "Desfaceți fiecare paranteză: ${a} - {b} + {c} - {d} + {e}$.",
            "placeholder": "= ?",
        },
    },
]
