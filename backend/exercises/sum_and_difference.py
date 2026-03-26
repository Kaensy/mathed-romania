"""
Exercise data: sum_and_difference
Topic 1.5 — Scăderea numerelor naturale

Category: sum_and_difference
Label (RO): Suma și diferența

Tiers:
  Easy   — Subtract sum-difference, find sum given difference and one number
  Medium — Given sum and difference find the numbers, three numbers with partial sums
  Hard   — Chain differences, three numbers with difference constraints

Usage:
    python manage.py load_exercises exercises.sum_and_difference
    python manage.py load_exercises exercises.sum_and_difference --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 5,
}

EXERCISES = [

    # ── EASY ─────────────────────────────────────────────────────────────────

    {
        "name": "Suma minus diferența a două numere",
        "category": "sum_and_difference",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Suma minus diferența a două numere",
            "type": "fill_blank",
            "question": "Scădeți din suma numerelor ${a}$ și ${b}$ diferența lor.",
            "params": {
                "a": {"type": "randint", "min": 200, "max": 5000},
                "b": {"type": "randint", "min": 100, "max": 199},
                "s": {"type": "computed", "expr": "{a} + {b}"},
                "d": {"type": "computed", "expr": "{a} - {b}"},
                "ans": {"type": "computed", "expr": "{s} - {d}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Suma: ${a} + {b} = {s}$. Diferența: ${a} - {b} = {d}$. Apoi scădeți: ${s} - {d}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Cu cât este mai mare suma decât diferența?",
        "category": "sum_and_difference",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Cu cât este mai mare suma decât diferența?",
            "type": "fill_blank",
            "question": "Cu cât este mai mare suma numerelor ${a}$ și ${b}$ decât diferența lor?",
            "params": {
                "a": {"type": "randint", "min": 500, "max": 9999},
                "b": {"type": "randint", "min": 100, "max": 499},
                "s": {"type": "computed", "expr": "{a} + {b}"},
                "d": {"type": "computed", "expr": "{a} - {b}"},
                "ans": {"type": "computed", "expr": "{s} - {d}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Suma $= {s}$, diferența $= {d}$. Rezultatul este $2 \\cdot {b}$ (dublul celui mai mic număr)!",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Diferența este D, un număr este A. Găsiți suma.",
        "category": "sum_and_difference",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Diferența este D, un număr este A. Găsiți suma.",
            "type": "fill_blank",
            "question": "Diferența a două numere naturale este ${d}$. Unul dintre numere este ${a}$. Calculați suma celor două numere.",
            "params": {
                "d": {"type": "randint", "min": 100, "max": 1500},
                "a": {"type": "randint", "min": 2000, "max": 5000},
                "b":    {"type": "computed", "expr": "{a} - {d}"},
                "sum1": {"type": "computed", "expr": "{a} + {b}"},
                "c":    {"type": "computed", "expr": "{a} + {d}"},
                "sum2": {"type": "computed", "expr": "{a} + {c}"},
            },
            "answer_expr": "{sum1}",
            "alt_answer_expr": "{sum2}",
            "follow_up_question": "Există și o altă posibilitate. Care este cealaltă sumă?",
            "answer_input": "number",
            "hint": "Atenție: celălalt număr poate fi ${a} - {d}$ sau ${a} + {d}$, deci există două sume posibile!",
            "placeholder": "Suma = ?",
        },
    },

    # ── MEDIUM ───────────────────────────────────────────────────────────────

    {
        "name": "Suma și diferența → cel mai mare număr",
        "category": "sum_and_difference",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Suma și diferența → cel mai mare număr",
            "type": "fill_blank",
            "question": "Suma a două numere naturale este ${s}$, iar diferența lor este ${d}$. Determinați cel mai mare număr.",
            "params": {
                "a": {"type": "randint", "min": 200, "max": 5000},
                "b": {"type": "randint", "min": 50, "max": 199},
                "s": {"type": "computed", "expr": "{a} + {b}"},
                "d": {"type": "computed", "expr": "{a} - {b}"},
            },
            "answer_expr": "{a}",
            "answer_input": "number",
            "hint": "Cel mai mare $= \\frac{{\\text{{suma}} + \\text{{diferența}}}}{{2}} = \\frac{{{s} + {d}}}{{2}}$.",
            "placeholder": "Cel mai mare = ?",
        },
    },
    {
        "name": "Suma și diferența → cel mai mic număr",
        "category": "sum_and_difference",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Suma și diferența → cel mai mic număr",
            "type": "fill_blank",
            "question": "Suma a două numere naturale este ${s}$, iar diferența lor este ${d}$. Determinați cel mai mic număr.",
            "params": {
                "a": {"type": "randint", "min": 200, "max": 5000},
                "b": {"type": "randint", "min": 50, "max": 199},
                "s": {"type": "computed", "expr": "{a} + {b}"},
                "d": {"type": "computed", "expr": "{a} - {b}"},
            },
            "answer_expr": "{b}",
            "answer_input": "number",
            "hint": "Cel mai mic $= \\frac{{\\text{{suma}} - \\text{{diferența}}}}{{2}} = \\frac{{{s} - {d}}}{{2}}$.",
            "placeholder": "Cel mai mic = ?",
        },
    },
    {
        "name": "Trei numere: suma totală + sumă parțială → al treilea",
        "category": "sum_and_difference",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Trei numere: suma totală + sumă parțială → al treilea",
            "type": "fill_blank",
            "question": "Suma a trei numere este ${total}$. Suma primelor două este ${s12}$. Care este al treilea număr?",
            "params": {
                "a": {"type": "randint", "min": 100, "max": 1000},
                "b": {"type": "randint", "min": 100, "max": 1000},
                "c": {"type": "randint", "min": 100, "max": 1000},
                "total": {"type": "computed", "expr": "{a} + {b} + {c}"},
                "s12":   {"type": "computed", "expr": "{a} + {b}"},
            },
            "answer_expr": "{c}",
            "answer_input": "number",
            "hint": "Al treilea număr $= {total} - {s12}$.",
            "placeholder": "Al treilea = ?",
        },
    },

    # ── HARD ──────────────────────────────────────────────────────────────────

    {
        "name": "Diferențe înlănțuite: a−b și b−c → a−c",
        "category": "sum_and_difference",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Diferențe înlănțuite: a−b și b−c → a−c",
            "type": "fill_blank",
            "question": "Dacă $a - b = {d1}$ și $b - c = {d2}$, determinați $a - c$.",
            "params": {
                "d1":  {"type": "randint", "min": 50, "max": 500},
                "d2":  {"type": "randint", "min": 50, "max": 500},
                "ans": {"type": "computed", "expr": "{d1} + {d2}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "$a - c = (a - b) + (b - c) = {d1} + {d2}$.",
            "placeholder": "a − c = ?",
        },
    },
    {
        "name": "Diferențe înlănțuite: a−c și b−c → a−b",
        "category": "sum_and_difference",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Diferențe înlănțuite: a−c și b−c → a−b",
            "type": "fill_blank",
            "question": "Dacă $a - c = {d1}$ și $b - c = {d2}$, determinați $a - b$.",
            "params": {
                "d1":  {"type": "randint", "min": 200, "max": 1000},
                "d2":  {"type": "randint", "min": 50, "max": 199},
                "ans": {"type": "computed", "expr": "{d1} - {d2}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "$a - b = (a - c) - (b - c) = {d1} - {d2}$.",
            "placeholder": "a − b = ?",
        },
    },
    {
        "name": "Trei numere: primul cu X și Y mai mare",
        "category": "sum_and_difference",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Trei numere: primul cu X și Y mai mare decât celelalte",
            "type": "fill_blank",
            "question": "Suma a trei numere este ${total}$. Primul este cu ${p}$ mai mare decât al doilea și cu ${q}$ mai mare decât al treilea. Determinați primul număr.",
            "params": {
                "first":  {"type": "randint", "min": 300, "max": 3000},
                "p":      {"type": "randint", "min": 50, "max": 500},
                "q":      {"type": "randint", "min": 50, "max": 500},
                "second": {"type": "computed", "expr": "{first} - {p}"},
                "third":  {"type": "computed", "expr": "{first} - {q}"},
                "total":  {"type": "computed", "expr": "{first} + {second} + {third}"},
            },
            "answer_expr": "{first}",
            "answer_input": "number",
            "hint": "Fie $a$ primul. Atunci: $a + (a - {p}) + (a - {q}) = {total}$, deci $3a = {total} + {p} + {q}$.",
            "placeholder": "Primul = ?",
        },
    },
]