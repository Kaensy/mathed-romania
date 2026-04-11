"""
Exercise data: find_x_division
Topic 1.7 — Împărțirea

Category: find_x_division
Label (RO): Aflarea necunoscutei (împărțire)

Tiers:
  Easy   — Direct equations: x:a=b, a:x=b
  Medium — Two-step equations: x:a+k=b, (x-k):a=b, a:x+k=b
  Hard   — Multi-step equations with nested operations

All templates guarantee exact division (natural number solutions) by
constructing the equations from a randomly chosen x.

Usage:
    python manage.py load_exercises exercises.find_x_division
    python manage.py load_exercises exercises.find_x_division --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 7,  # "Împărțirea"
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Direct equations
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Necunoscută: x : a = b",
        "category": "find_x_division",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: x : a = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  $x : {a} = {b}$",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 50},
                "b": {"type": "randint", "min": 2, "max": 100},
                "x": {"type": "computed", "expr": "{a} * {b}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Dacă $x : {a} = {b}$, atunci $x = {a} \\cdot {b}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: a : x = b",
        "category": "find_x_division",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: a : x = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${a} : x = {b}$",
            "params": {
                "x": {"type": "randint", "min": 2, "max": 50},
                "b": {"type": "randint", "min": 2, "max": 100},
                "a": {"type": "computed", "expr": "{x} * {b}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Dacă ${a} : x = {b}$, atunci $x = {a} : {b}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: x · a = b (cu împărțire)",
        "category": "find_x_division",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: x · a = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  $x \\cdot {a} = {b}$",
            "params": {
                "x": {"type": "randint", "min": 2, "max": 100},
                "a": {"type": "randint", "min": 2, "max": 50},
                "b": {"type": "computed", "expr": "{x} * {a}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Dacă $x \\cdot {a} = {b}$, atunci $x = {b} : {a}$.",
            "placeholder": "x = ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Two-step equations
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Necunoscută: x : a + k = b",
        "category": "find_x_division",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: x : a + k = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$:  $x : {a} + {k} = {b}$",
            "params": {
                "a":   {"type": "randint", "min": 3, "max": 20},
                "q":   {"type": "randint", "min": 5, "max": 50},
                "k":   {"type": "randint", "min": 5, "max": 100},
                "x":   {"type": "computed", "expr": "{a} * {q}"},
                "b":   {"type": "computed", "expr": "{q} + {k}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Mai întâi aflați $x : {a} = {b} - {k} = {q}$, apoi $x = {a} \\cdot {q}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: x : a − k = b",
        "category": "find_x_division",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: x : a − k = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$:  $x : {a} - {k} = {b}$",
            "params": {
                "a": {"type": "randint", "min": 3, "max": 20},
                "b": {"type": "randint", "min": 5, "max": 50},
                "k": {"type": "randint", "min": 3, "max": 20},
                "q": {"type": "computed", "expr": "{b} + {k}"},
                "x": {"type": "computed", "expr": "{a} * {q}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Mai întâi aflați $x : {a} = {b} + {k} = {q}$, apoi $x = {a} \\cdot {q}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: (x + k) : a = b",
        "category": "find_x_division",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: (x + k) : a = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$:  $(x + {k}) : {a} = {b}$",
            "params": {
            "a":     {"type": "randint", "min": 3, "max": 20},
            "b":     {"type": "randint", "min": 5, "max": 50},
            "k":     {"type": "randint", "min": 5, "max": 100},
            "total": {"type": "computed", "expr": "{a} * {b}"},
            "x":     {"type": "computed", "expr": "{total} - {k}"},
        },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Mai întâi aflați $x + {k} = {a} \\cdot {b} = {total}$, apoi $x = {total} - {k}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: a : x + k = b",
        "category": "find_x_division",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: a : x + k = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$:  ${a} : x + {k} = {b}$",
            "params": {
                "x": {"type": "randint", "min": 2, "max": 30},
                "q": {"type": "randint", "min": 3, "max": 30},
                "k": {"type": "randint", "min": 5, "max": 100},
                "a": {"type": "computed", "expr": "{x} * {q}"},
                "b": {"type": "computed", "expr": "{q} + {k}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Mai întâi aflați ${a} : x = {b} - {k} = {q}$, apoi $x = {a} : {q}$.",
            "placeholder": "x = ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Multi-step nested equations
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Necunoscută: (x − k) : a = b",
        "category": "find_x_division",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: (x − k) : a = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$:  $(x - {k}) : {a} = {b}$",
            "params": {
                "a":    {"type": "randint", "min": 3, "max": 20},
                "b":    {"type": "randint", "min": 5, "max": 50},
                "k":    {"type": "randint", "min": 10, "max": 200},
                "diff": {"type": "computed", "expr": "{a} * {b}"},
                "x":    {"type": "computed", "expr": "{diff} + {k}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Mai întâi aflați $x - {k} = {a} \\cdot {b} = {diff}$, apoi $x = {diff} + {k}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: (x : a + k) · m = b",
        "category": "find_x_division",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: (x : a + k) · m = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$:  $(x : {a} + {k}) \\cdot {m} = {b}$",
            "params": {
                "a":     {"type": "randint", "min": 3, "max": 15},
                "q":     {"type": "randint", "min": 3, "max": 20},
                "k":     {"type": "randint", "min": 2, "max": 20},
                "m":     {"type": "randint", "min": 2, "max": 15},
                "x":     {"type": "computed", "expr": "{a} * {q}"},
                "inner": {"type": "computed", "expr": "{q} + {k}"},
                "b":     {"type": "computed", "expr": "{inner} * {m}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Dezvoltați din exterior: paranteza = ${b} : {m} = {inner}$, apoi $x : {a} = {inner} - {k} = {q}$, deci $x = {a} \\cdot {q}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: (a · x + b · x) : k = c",
        "category": "find_x_division",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută cu factor comun de x",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$:  $({a} \\cdot x + {b} \\cdot x) : {k} = {c}$",
            "params": {
                "x":     {"type": "randint", "min": 3, "max": 30},
                "k":     {"type": "randint", "min": 2, "max": 10},
                "a_sub": {"type": "randint", "min": 1, "max": 8},
                "b_sub": {"type": "randint", "min": 1, "max": 8},
                "a":     {"type": "computed", "expr": "{a_sub} * {k}"},
                "b":     {"type": "computed", "expr": "{b_sub} * {k}"},
                "c":     {"type": "computed", "expr": "({a_sub} + {b_sub}) * {x}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Scoateți $x$ ca factor comun: $({a} + {b}) \\cdot x : {k} = {c}$. Simplificați: $({a} + {b}) : {k}$ și obțineți $x$.",
            "placeholder": "x = ?",
        },
    },
]
