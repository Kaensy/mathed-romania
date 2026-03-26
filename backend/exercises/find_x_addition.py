"""
Exercise data: find_x_addition
Topic 1.4 — Adunarea numerelor naturale

Category: find_x_addition
Label (RO): Aflarea necunoscutei

Tiers:
  Easy   — Simple equations: x+a=b, a+x=b, (x+a)+b=c, k·x+a=b
  Medium — Multi-term equations, x buried among terms
  Hard   — Gauss sub-sums in equations, missing sequence term

Usage:
    python manage.py load_exercises exercises.find_x_addition
    python manage.py load_exercises exercises.find_x_addition --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 4,  # "Adunarea numerelor naturale"
}

EXERCISES = [

    # ── EASY ─────────────────────────────────────────────────────────────────

    {
        "name": "Necunoscută: x + a = b",
        "category": "find_x_addition",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: x + a = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  $x + {a} = {b}$",
            "params": {
                "x": {"type": "randint", "min": 100, "max": 9999},
                "a": {"type": "randint", "min": 100, "max": 9999},
                "b": {"type": "computed", "expr": "{x} + {a}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Dacă $x + {a} = {b}$, atunci $x = {b} - {a}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: a + x = b",
        "category": "find_x_addition",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: a + x = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${a} + x = {b}$",
            "params": {
                "x": {"type": "randint", "min": 100, "max": 9999},
                "a": {"type": "randint", "min": 100, "max": 9999},
                "b": {"type": "computed", "expr": "{a} + {x}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Dacă ${a} + x = {b}$, atunci $x = {b} - {a}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: (x + a) + b = c",
        "category": "find_x_addition",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: (x + a) + b = c",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  $(x + {a}) + {b} = {c}$",
            "params": {
                "x": {"type": "randint", "min": 10, "max": 999},
                "a": {"type": "randint", "min": 10, "max": 200},
                "b": {"type": "randint", "min": 10, "max": 200},
                "c": {"type": "computed", "expr": "{x} + {a} + {b}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Calculați mai întâi $x + {a} = {c} - {b}$, apoi aflați $x$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: k·x + a = b",
        "category": "find_x_addition",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: k·x + a = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${k} \\cdot x + {a} = {b}$",
            "params": {
                "x": {"type": "randint", "min": 10, "max": 500},
                "k": {"type": "randint", "min": 2, "max": 5},
                "a": {"type": "randint", "min": 50, "max": 999},
                "b": {"type": "computed", "expr": "{k} * {x} + {a}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Mai întâi aflați ${k} \\cdot x = {b} - {a}$, apoi împărțiți la ${k}$.",
            "placeholder": "x = ?",
        },
    },

    # ── MEDIUM ───────────────────────────────────────────────────────────────

    {
        "name": "Necunoscută: x + a + b + c = d",
        "category": "find_x_addition",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: x + a + b + c = d",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  $x + {a} + {b} + {c} = {d}$",
            "params": {
                "x": {"type": "randint", "min": 100, "max": 5000},
                "a": {"type": "randint", "min": 100, "max": 2000},
                "b": {"type": "randint", "min": 100, "max": 2000},
                "c": {"type": "randint", "min": 100, "max": 2000},
                "d": {"type": "computed", "expr": "{x} + {a} + {b} + {c}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Adunați termenii cunoscuți: ${a} + {b} + {c}$, apoi scădeți din ${d}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: x printre 5 termeni",
        "category": "find_x_addition",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: x printre 5 termeni",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${a} + {b} + x + {c} + {d} = {total}$",
            "params": {
                "x": {"type": "randint", "min": 100, "max": 5000},
                "a": {"type": "randint", "min": 100, "max": 3000},
                "b": {"type": "randint", "min": 100, "max": 3000},
                "c": {"type": "randint", "min": 100, "max": 3000},
                "d": {"type": "randint", "min": 100, "max": 3000},
                "total": {"type": "computed", "expr": "{a} + {b} + {x} + {c} + {d}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Adunați toți termenii cunoscuți: ${a} + {b} + {c} + {d}$, apoi scădeți din ${total}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: a + (x + b) + c = d",
        "category": "find_x_addition",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: a + (x + b) + c = d",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${a} + (x + {b}) + {c} = {d}$",
            "params": {
                "x": {"type": "randint", "min": 10, "max": 2000},
                "a": {"type": "randint", "min": 10, "max": 500},
                "b": {"type": "randint", "min": 10, "max": 500},
                "c": {"type": "randint", "min": 10, "max": 500},
                "d": {"type": "computed", "expr": "{a} + {x} + {b} + {c}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Parantezele nu schimbă rezultatul! ${a} + (x + {b}) + {c} = {a} + x + {b} + {c}$. Adunați termenii cunoscuți și scădeți din ${d}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: 6 termeni cu x + sumă rotundă",
        "category": "find_x_addition",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: 6 termeni cu x + sumă rotundă",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${a} + {b} + {c} + x + {d} + {e} = {total}$",
            "params": {
                "x":     {"type": "randint", "min": 50, "max": 3000},
                "a":     {"type": "randint", "min": 20, "max": 500},
                "b":     {"type": "randint", "min": 20, "max": 500},
                "c":     {"type": "randint", "min": 20, "max": 500},
                "d":     {"type": "randint", "min": 20, "max": 500},
                "e":     {"type": "randint", "min": 20, "max": 500},
                "total": {"type": "computed", "expr": "{a} + {b} + {c} + {x} + {d} + {e}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Adunați cei 5 termeni cunoscuți: ${a} + {b} + {c} + {d} + {e}$, apoi scădeți suma din ${total}$.",
            "placeholder": "x = ?",
        },
    },

    # ── HARD ─────────────────────────────────────────────────────────────────

    {
        "name": "Necunoscută: 1+2+...+n + x = total",
        "category": "find_x_addition",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: 1+2+...+n + x = total",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  $1 + 2 + 3 + \\ldots + {n} + x = {total}$",
            "params": {
                "n":       {"type": "randint", "min": 8, "max": 20},
                "x":       {"type": "randint", "min": 500, "max": 5000},
                "gauss":   {"type": "computed", "expr": "{n} * ({n} + 1) // 2"},
                "total":   {"type": "computed", "expr": "{gauss} + {x}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Calculați mai întâi suma $1 + 2 + \\ldots + {n}$ folosind formula lui Gauss: $S = \\frac{{{n} \\cdot ({n}+1)}}{{2}} = {gauss}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: termen lipsă din secvență",
        "category": "find_x_addition",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: termen lipsă din secvență",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  $1 + 2 + 3 + 4 + x + 6 + 7 + 8 + 9 + {k} = {total}$",
            "params": {
                "x":       {"type": "randint", "min": 100, "max": 9999},
                "k":       {"type": "randint", "min": 10, "max": 99},
                "known":   {"type": "computed", "expr": "1 + 2 + 3 + 4 + 6 + 7 + 8 + 9 + {k}"},
                "total":   {"type": "computed", "expr": "{known} + {x}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Adunați toți termenii cunoscuți: $1+2+3+4+6+7+8+9+{k} = {known}$, apoi $x = {total} - {known}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: k·x + a + b = c (mare)",
        "category": "find_x_addition",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: k·x + a + b = c (mare)",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${k} \\cdot x + {a} + {b} = {c}$",
            "params": {
                "x": {"type": "randint", "min": 100, "max": 5000},
                "k": {"type": "randint", "min": 2, "max": 7},
                "a": {"type": "randint", "min": 100, "max": 5000},
                "b": {"type": "randint", "min": 100, "max": 5000},
                "c": {"type": "computed", "expr": "{k} * {x} + {a} + {b}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Mai întâi calculați ${k} \\cdot x = {c} - {a} - {b}$, apoi împărțiți la ${k}$.",
            "placeholder": "x = ?",
        },
    },
]
