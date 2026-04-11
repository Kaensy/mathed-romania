"""
Exercise data: division_remainder_compute
Topic 1.7 — Împărțirea (lesson 7.2: Împărțirea cu rest)

Category: division_remainder_compute
Label (RO): Calcul cu rest

Tiers:
  Easy   — Small dividends/divisors, single-digit divisors
  Medium — Larger dividends (4-5 digits) with 2-digit divisors
  Hard   — Very large dividends with 3-digit divisors, edge cases

All templates are multi_fill_blank with two fields: câtul (quotient) and
restul (remainder). Every division produces a nonzero remainder to keep
the exercise meaningful (otherwise it would be an exact division).

Usage:
    python manage.py load_exercises exercises.division_remainder_compute
    python manage.py load_exercises exercises.division_remainder_compute --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 7,  # "Împărțirea"
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Small dividends and single-digit divisors
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Cât și rest: 3 cifre : 1 cifră",
        "category": "division_remainder_compute",
        "difficulty": "easy",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Cât și rest: 3 cifre : 1 cifră",
            "type": "multi_fill_blank",
            "question": "Calculați câtul și restul împărțirii:  ${a} : {b}$",
            "params": {
                "b": {"type": "randint", "min": 3, "max": 9},
                "q": {"type": "randint", "min": 20, "max": 199},
                "r": {"type": "randint", "min": 1, "max": "{b} - 1"},
                "a": {"type": "computed", "expr": "{b} * {q} + {r}"},
            },
            "fields": [
                {"key": "cat",  "label": "Câtul",  "answer_expr": "{q}"},
                {"key": "rest", "label": "Restul", "answer_expr": "{r}"},
            ],
            "answer_input": "number",
            "hint": "Efectuați împărțirea. Amintiți-vă că restul trebuie să fie mai mic decât ${b}$.",
        },
    },
    {
        "name": "Cât și rest: 3 cifre : 2 cifre",
        "category": "division_remainder_compute",
        "difficulty": "easy",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Cât și rest: 3 cifre : 2 cifre",
            "type": "multi_fill_blank",
            "question": "Calculați câtul și restul împărțirii:  ${a} : {b}$",
            "params": {
                "b": {"type": "randint", "min": 11, "max": 29},
                "q": {"type": "randint", "min": 10, "max": 40},
                "r": {"type": "randint", "min": 1, "max": 10},
                "a": {"type": "computed", "expr": "{b} * {q} + {r}"},
            },
            "fields": [
                {"key": "cat",  "label": "Câtul",  "answer_expr": "{q}"},
                {"key": "rest", "label": "Restul", "answer_expr": "{r}"},
            ],
            "answer_input": "number",
            "hint": "Efectuați împărțirea. Restul trebuie să fie mai mic decât ${b}$.",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Larger dividends
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Cât și rest: 4-5 cifre : 1 cifră",
        "category": "division_remainder_compute",
        "difficulty": "medium",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Cât și rest: 4-5 cifre : 1 cifră",
            "type": "multi_fill_blank",
            "question": "Calculați câtul și restul împărțirii:  ${a} : {b}$",
            "params": {
                "b": {"type": "randint", "min": 3, "max": 9},
                "q": {"type": "randint", "min": 1000, "max": 19999},
                "r": {"type": "randint", "min": 1, "max": 2},
                "a": {"type": "computed", "expr": "{b} * {q} + {r}"},
            },
            "fields": [
                {"key": "cat",  "label": "Câtul",  "answer_expr": "{q}"},
                {"key": "rest", "label": "Restul", "answer_expr": "{r}"},
            ],
            "answer_input": "number",
            "hint": "Efectuați împărțirea în coloană. Restul trebuie să fie mai mic decât ${b}$.",
        },
    },
    {
        "name": "Cât și rest: 4-5 cifre : 2 cifre",
        "category": "division_remainder_compute",
        "difficulty": "medium",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Cât și rest: 4-5 cifre : 2 cifre",
            "type": "multi_fill_blank",
            "question": "Calculați câtul și restul împărțirii:  ${a} : {b}$",
            "params": {
                "b": {"type": "randint", "min": 12, "max": 99},
                "q": {"type": "randint", "min": 100, "max": 999},
                "r": {"type": "randint", "min": 1, "max": 10},
                "a": {"type": "computed", "expr": "{b} * {q} + {r}"},
            },
            "fields": [
                {"key": "cat",  "label": "Câtul",  "answer_expr": "{q}"},
                {"key": "rest", "label": "Restul", "answer_expr": "{r}"},
            ],
            "answer_input": "number",
            "hint": "Efectuați împărțirea în coloană. Restul trebuie să fie mai mic decât ${b}$.",
        },
    },
    {
        "name": "Cât și rest: 5 cifre : 2 cifre",
        "category": "division_remainder_compute",
        "difficulty": "medium",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Cât și rest: 5 cifre : 2 cifre",
            "type": "multi_fill_blank",
            "question": "Calculați câtul și restul împărțirii:  ${a} : {b}$",
            "params": {
                "b": {"type": "randint", "min": 20, "max": 99},
                "q": {"type": "randint", "min": 500, "max": 4999},
                "r": {"type": "randint", "min": 1, "max": 15},
                "a": {"type": "computed", "expr": "{b} * {q} + {r}"},
            },
            "fields": [
                {"key": "cat",  "label": "Câtul",  "answer_expr": "{q}"},
                {"key": "rest", "label": "Restul", "answer_expr": "{r}"},
            ],
            "answer_input": "number",
            "hint": "Efectuați împărțirea în coloană. Verificați: deîmpărțit = împărțitor · cât + rest.",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Very large dividends, 3-digit divisors
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Cât și rest: 5-6 cifre : 3 cifre",
        "category": "division_remainder_compute",
        "difficulty": "hard",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Cât și rest: 5-6 cifre : 3 cifre",
            "type": "multi_fill_blank",
            "question": "Calculați câtul și restul împărțirii:  ${a} : {b}$",
            "params": {
                "b": {"type": "randint", "min": 100, "max": 999},
                "q": {"type": "randint", "min": 100, "max": 999},
                "r": {"type": "randint", "min": 1, "max": 50},
                "a": {"type": "computed", "expr": "{b} * {q} + {r}"},
            },
            "fields": [
                {"key": "cat",  "label": "Câtul",  "answer_expr": "{q}"},
                {"key": "rest", "label": "Restul", "answer_expr": "{r}"},
            ],
            "answer_input": "number",
            "hint": "Efectuați împărțirea în coloană. Verificați cu proba: ${b} \\cdot q + r = {a}$.",
        },
    },
    {
        "name": "Cât și rest: dividend mare, cât mic",
        "category": "division_remainder_compute",
        "difficulty": "hard",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Cât și rest: dividend mare, cât mic",
            "type": "multi_fill_blank",
            "question": "Calculați câtul și restul împărțirii:  ${a} : {b}$",
            "params": {
                "b": {"type": "randint", "min": 500, "max": 9999},
                "q": {"type": "randint", "min": 2, "max": 50},
                "r": {"type": "randint", "min": 1, "max": 100},
                "a": {"type": "computed", "expr": "{b} * {q} + {r}"},
            },
            "fields": [
                {"key": "cat",  "label": "Câtul",  "answer_expr": "{q}"},
                {"key": "rest", "label": "Restul", "answer_expr": "{r}"},
            ],
            "answer_input": "number",
            "hint": "Estimați de câte ori intră ${b}$ în ${a}$. Restul este ce rămâne după scădere.",
        },
    },
    {
        "name": "Cât și rest: cazuri speciale (cât=0)",
        "category": "division_remainder_compute",
        "difficulty": "hard",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Cât și rest: cazuri speciale (cât = 0)",
            "type": "multi_fill_blank",
            "question": "Calculați câtul și restul împărțirii:  ${a} : {b}$",
            "params": {
                "b": {"type": "randint", "min": 100, "max": 999},
                "a": {"type": "randint", "min": 1, "max": 99},
            },
            "fields": [
                {"key": "cat",  "label": "Câtul",  "answer_expr": "0"},
                {"key": "rest", "label": "Restul", "answer_expr": "{a}"},
            ],
            "answer_input": "number",
            "hint": "Când deîmpărțitul (${a}$) este mai mic decât împărțitorul (${b}$), câtul este $0$ și restul este chiar deîmpărțitul.",
        },
    },
]
