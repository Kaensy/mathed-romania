"""
Exercise data: find_x_subtraction
Topic 1.5 — Scăderea numerelor naturale

Category: find_x_subtraction
Label (RO): Aflarea necunoscutei (scădere)

Tiers:
  Easy   — Simple: a+x=b, a−x=b, x−a=b
  Medium — Multi-term: x among several terms, mixed +/−
  Hard   — Complex: x with nested operations, larger numbers

Usage:
    python manage.py load_exercises exercises.find_x_subtraction
    python manage.py load_exercises exercises.find_x_subtraction --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 5,
}

EXERCISES = [

    # ── EASY ─────────────────────────────────────────────────────────────────

    {
        "name": "Necunoscută: a − x = b",
        "category": "find_x_subtraction",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: a − x = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${a} - x = {b}$",
            "params": {
                "x": {"type": "randint", "min": 100, "max": 5000},
                "b": {"type": "randint", "min": 100, "max": 5000},
                "a": {"type": "computed", "expr": "{b} + {x}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Dacă ${a} - x = {b}$, atunci $x = {a} - {b}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: x − a = b",
        "category": "find_x_subtraction",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: x − a = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  $x - {a} = {b}$",
            "params": {
                "x": {"type": "randint", "min": 500, "max": 9999},
                "a": {"type": "randint", "min": 100, "max": 499},
                "b": {"type": "computed", "expr": "{x} - {a}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Dacă $x - {a} = {b}$, atunci $x = {b} + {a}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: a + x = b (scădere)",
        "category": "find_x_subtraction",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: a + x = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${a} + x = {b}$",
            "params": {
                "x": {"type": "randint", "min": 100, "max": 5000},
                "a": {"type": "randint", "min": 100, "max": 5000},
                "b": {"type": "computed", "expr": "{a} + {x}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Dacă ${a} + x = {b}$, atunci $x = {b} - {a}$.",
            "placeholder": "x = ?",
        },
    },

    # ── MEDIUM ───────────────────────────────────────────────────────────────

    {
        "name": "Necunoscută: x − a − b = c",
        "category": "find_x_subtraction",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: x − a − b = c",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  $x - {a} - {b} = {c}$",
            "params": {
                "x": {"type": "randint", "min": 1000, "max": 20000},
                "a": {"type": "randint", "min": 100, "max": 3000},
                "b": {"type": "randint", "min": 100, "max": 3000},
                "c": {"type": "computed", "expr": "{x} - {a} - {b}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "$x = {c} + {a} + {b}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: a + x − b = c",
        "category": "find_x_subtraction",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: a + x − b = c",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${a} + x - {b} = {c}$",
            "params": {
                "x": {"type": "randint", "min": 500, "max": 10000},
                "a": {"type": "randint", "min": 100, "max": 5000},
                "b": {"type": "randint", "min": 100, "max": 3000},
                "c": {"type": "computed", "expr": "{a} + {x} - {b}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "$x = {c} - {a} + {b}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: a − x + b = c",
        "category": "find_x_subtraction",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: a − x + b = c",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${a} - x + {b} = {c}$",
            "params": {
                "x": {"type": "randint", "min": 100, "max": 5000},
                "a": {"type": "randint", "min": 3000, "max": 10000},
                "b": {"type": "randint", "min": 100, "max": 3000},
                "c": {"type": "computed", "expr": "{a} - {x} + {b}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "$x = {a} + {b} - {c}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: a + x + b = c (mari)",
        "category": "find_x_subtraction",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: a + x + b = c (mari)",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${a} + x + {b} + {d} = {c}$",
            "params": {
                "x": {"type": "randint", "min": 500, "max": 5000},
                "a": {"type": "randint", "min": 100, "max": 3000},
                "b": {"type": "randint", "min": 100, "max": 2000},
                "d": {"type": "randint", "min": 100, "max": 2000},
                "c": {"type": "computed", "expr": "{a} + {x} + {b} + {d}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Adunați termenii cunoscuți: ${a} + {b} + {d}$, apoi scădeți din ${c}$.",
            "placeholder": "x = ?",
        },
    },

    # ── HARD ──────────────────────────────────────────────────────────────────

    {
        "name": "Necunoscută: a − (x − b) = c",
        "category": "find_x_subtraction",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: a − (x − b) = c",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${a} - (x - {b}) = {c}$",
            "params": {
                "x": {"type": "randint", "min": 500, "max": 5000},
                "b": {"type": "randint", "min": 100, "max": 2000},
                "a": {"type": "randint", "min": 5000, "max": 15000},
                "c": {"type": "computed", "expr": "{a} - {x} + {b}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Desfaceți paranteza: ${a} - x + {b} = {c}$, deci $x = {a} + {b} - {c}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: (a − x) + b − c = d",
        "category": "find_x_subtraction",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: (a − x) + b − c = d",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  $({a} - x) + {b} - {c} = {d}$",
            "params": {
                "x": {"type": "randint", "min": 100, "max": 5000},
                "a": {"type": "randint", "min": 5000, "max": 15000},
                "b": {"type": "randint", "min": 100, "max": 3000},
                "c": {"type": "randint", "min": 100, "max": 2000},
                "d": {"type": "computed", "expr": "{a} - {x} + {b} - {c}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Simplificați: ${a} - x + {b} - {c} = {d}$, deci $x = {a} + {b} - {c} - {d}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: a − x − b − c = d (multe terme)",
        "category": "find_x_subtraction",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: a − x − b − c = d",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${a} - x - {b} - {c} = {d}$",
            "params": {
                "x": {"type": "randint", "min": 500, "max": 5000},
                "a": {"type": "randint", "min": 10000, "max": 30000},
                "b": {"type": "randint", "min": 500, "max": 5000},
                "c": {"type": "randint", "min": 500, "max": 5000},
                "d": {"type": "computed", "expr": "{a} - {x} - {b} - {c}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "$x = {a} - {b} - {c} - {d}$.",
            "placeholder": "x = ?",
        },
    },
]
