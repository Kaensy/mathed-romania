"""
Exercise data: arithmetic_sequence
Topic 1.4 — Adunarea numerelor naturale

Category: arithmetic_sequence
Label (RO): Șir aritmetic

Tiers:
  Easy   — Find next term, find the step, complete a missing term
  Medium — Find nth term, how many terms
  Hard   — Sum of first n terms, reverse problems

Usage:
    python manage.py load_exercises exercises.arithmetic_sequence
    python manage.py load_exercises exercises.arithmetic_sequence --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 4,
}

EXERCISES = [

    # ── EASY ─────────────────────────────────────────────────────────────────

    {
        "name": "Șir aritmetic: următorul termen",
        "category": "arithmetic_sequence",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Șir aritmetic: următorul termen",
            "type": "fill_blank",
            "question": "Ce număr urmează în șirul: ${a1}$, ${a2}$, ${a3}$, ${a4}$, $?$",
            "params": {
                "a1":  {"type": "randint", "min": 1, "max": 50},
                "d":   {"type": "randint", "min": 2, "max": 15},
                "a2":  {"type": "computed", "expr": "{a1} + {d}"},
                "a3":  {"type": "computed", "expr": "{a1} + 2 * {d}"},
                "a4":  {"type": "computed", "expr": "{a1} + 3 * {d}"},
                "ans": {"type": "computed", "expr": "{a1} + 4 * {d}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Diferența dintre termeni consecutivi este ${d}$. Adăugați ${d}$ la ultimul termen.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Șir aritmetic: găsește rația",
        "category": "arithmetic_sequence",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Șir aritmetic: găsește rația",
            "type": "fill_blank",
            "question": "Care este rația (diferența constantă) a șirului: ${a1}$, ${a2}$, ${a3}$, ${a4}$, $\\ldots$ ?",
            "params": {
                "a1":  {"type": "randint", "min": 1, "max": 50},
                "d":   {"type": "randint", "min": 2, "max": 20},
                "a2":  {"type": "computed", "expr": "{a1} + {d}"},
                "a3":  {"type": "computed", "expr": "{a1} + 2 * {d}"},
                "a4":  {"type": "computed", "expr": "{a1} + 3 * {d}"},
            },
            "answer_expr": "{d}",
            "answer_input": "number",
            "hint": "Scădeți doi termeni consecutivi: ${a2} - {a1} = ?$",
            "placeholder": "d = ?",
        },
    },
    {
        "name": "Șir aritmetic: termen lipsă",
        "category": "arithmetic_sequence",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Șir aritmetic: termen lipsă",
            "type": "fill_blank",
            "question": "Completați termenul lipsă din șirul: ${a1}$, ${a2}$, $?$, ${a4}$, ${a5}$",
            "params": {
                "a1":  {"type": "randint", "min": 1, "max": 50},
                "d":   {"type": "randint", "min": 2, "max": 15},
                "a2":  {"type": "computed", "expr": "{a1} + {d}"},
                "ans": {"type": "computed", "expr": "{a1} + 2 * {d}"},
                "a4":  {"type": "computed", "expr": "{a1} + 3 * {d}"},
                "a5":  {"type": "computed", "expr": "{a1} + 4 * {d}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Rația este ${d}$. Termenul lipsă este ${a2} + {d}$.",
            "placeholder": "= ?",
        },
    },

    # ── MEDIUM ───────────────────────────────────────────────────────────────

    {
        "name": "Șir aritmetic: al n-lea termen",
        "category": "arithmetic_sequence",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Șir aritmetic: al n-lea termen",
            "type": "fill_blank",
            "question": "Fie șirul de numere: ${a1}$, ${a2}$, ${a3}$, ${a4}$, $\\ldots$ Găsiți al ${n}$-lea termen al șirului.",
            "params": {
                "a1":  {"type": "randint", "min": 1, "max": 20},
                "d":   {"type": "randint", "min": 2, "max": 10},
                "a2":  {"type": "computed", "expr": "{a1} + {d}"},
                "a3":  {"type": "computed", "expr": "{a1} + 2 * {d}"},
                "a4":  {"type": "computed", "expr": "{a1} + 3 * {d}"},
                "n":   {"type": "randint", "min": 15, "max": 40},
                "ans": {"type": "computed", "expr": "{a1} + ({n} - 1) * {d}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Rația șirului este $d = {d}$. Termenul al $n$-lea: $a_n = {a1} + (n-1) \\cdot {d}$.",
            "placeholder": "a_n = ?",
        },
    },
    {
        "name": "Șir aritmetic: câți termeni are",
        "category": "arithmetic_sequence",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Șir aritmetic: câți termeni are",
            "type": "fill_blank",
            "question": "Fie șirul: ${a1}$, ${a2}$, ${a3}$, $\\ldots$, ${last}$. Câți termeni are acest șir?",
            "params": {
                "a1":   {"type": "randint", "min": 1, "max": 20},
                "d":    {"type": "randint", "min": 2, "max": 10},
                "n":    {"type": "randint", "min": 10, "max": 30},
                "a2":   {"type": "computed", "expr": "{a1} + {d}"},
                "a3":   {"type": "computed", "expr": "{a1} + 2 * {d}"},
                "last": {"type": "computed", "expr": "{a1} + ({n} - 1) * {d}"},
                "ans":  {"type": "computed", "expr": "{n}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Rația este $d = {d}$. Numărul de termeni: $n = \\frac{{{last} - {a1}}}{{{d}}} + 1$.",
            "placeholder": "n = ?",
        },
    },
    {
        "name": "Șir aritmetic: găsește primul termen",
        "category": "arithmetic_sequence",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Șir aritmetic: găsește primul termen",
            "type": "fill_blank",
            "question": "Un șir aritmetic are rația ${d}$ și al ${n}$-lea termen este ${an}$. Care este primul termen?",
            "params": {
                "a1":  {"type": "randint", "min": 1, "max": 30},
                "d":   {"type": "randint", "min": 2, "max": 10},
                "n":   {"type": "randint", "min": 10, "max": 25},
                "an":  {"type": "computed", "expr": "{a1} + ({n} - 1) * {d}"},
            },
            "answer_expr": "{a1}",
            "answer_input": "number",
            "hint": "$a_n = a_1 + (n-1) \\cdot d$, deci $a_1 = {an} - ({n}-1) \\cdot {d}$.",
            "placeholder": "a₁ = ?",
        },
    },

    # ── HARD ─────────────────────────────────────────────────────────────────

    {
        "name": "Șir aritmetic: suma primilor n termeni",
        "category": "arithmetic_sequence",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Șir aritmetic: suma primilor n termeni",
            "type": "fill_blank",
            "question": "Fie șirul de numere: ${a1}$, ${a2}$, ${a3}$, ${a4}$, $\\ldots$ Calculați suma primilor ${n}$ termeni ai șirului.",
            "params": {
                "a1":   {"type": "randint", "min": 1, "max": 15},
                "d":    {"type": "randint", "min": 2, "max": 8},
                "a2":   {"type": "computed", "expr": "{a1} + {d}"},
                "a3":   {"type": "computed", "expr": "{a1} + 2 * {d}"},
                "a4":   {"type": "computed", "expr": "{a1} + 3 * {d}"},
                "n":    {"type": "randint", "min": 10, "max": 25},
                "last": {"type": "computed", "expr": "{a1} + ({n} - 1) * {d}"},
                "ans":  {"type": "computed", "expr": "{n} * ({a1} + {last}) // 2"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Ultimul termen: $a_{{{n}}} = {last}$. Suma: $S = \\frac{{{n} \\cdot ({a1} + {last})}}{{2}}$.",
            "placeholder": "S = ?",
        },
    },
    {
        "name": "Șir aritmetic: găsește rația din doi termeni",
        "category": "arithmetic_sequence",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Șir aritmetic: găsește rația din doi termeni",
            "type": "fill_blank",
            "question": "Într-un șir aritmetic, al ${p}$-lea termen este ${ap}$ și al ${q}$-lea termen este ${aq}$. Care este rația șirului?",
            "params": {
                "a1":  {"type": "randint", "min": 1, "max": 20},
                "d":   {"type": "randint", "min": 2, "max": 10},
                "p":   {"type": "randint", "min": 3, "max": 8},
                "q":   {"type": "randint", "min": 15, "max": 30},
                "ap":  {"type": "computed", "expr": "{a1} + ({p} - 1) * {d}"},
                "aq":  {"type": "computed", "expr": "{a1} + ({q} - 1) * {d}"},
                "diff": {"type": "computed", "expr": "{q} - {p}"},
            },
            "answer_expr": "{d}",
            "answer_input": "number",
            "hint": "$d = \\frac{{a_{{{q}}} - a_{{{p}}}}}{{{q} - {p}}} = \\frac{{{aq} - {ap}}}{{{diff}}}$.",
            "placeholder": "d = ?",
        },
    },
    {
        "name": "Șir aritmetic: al câtelea termen este X?",
        "category": "arithmetic_sequence",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Șir aritmetic: al câtelea termen este X?",
            "type": "fill_blank",
            "question": "Fie șirul: ${a1}$, ${a2}$, ${a3}$, $\\ldots$ Al câtelea termen al șirului este ${target}$?",
            "params": {
                "a1":     {"type": "randint", "min": 1, "max": 15},
                "d":      {"type": "randint", "min": 2, "max": 10},
                "a2":     {"type": "computed", "expr": "{a1} + {d}"},
                "a3":     {"type": "computed", "expr": "{a1} + 2 * {d}"},
                "n":      {"type": "randint", "min": 15, "max": 50},
                "target": {"type": "computed", "expr": "{a1} + ({n} - 1) * {d}"},
            },
            "answer_expr": "{n}",
            "answer_input": "number",
            "hint": "Rația este $d = {d}$. Rezolvați: ${a1} + (n-1) \\cdot {d} = {target}$.",
            "placeholder": "n = ?",
        },
    },
]
