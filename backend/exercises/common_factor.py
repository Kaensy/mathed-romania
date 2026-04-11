"""
Exercise data: common_factor
Topic 1.6 — Înmulțirea numerelor naturale: distributivitate și factori comuni

Category: common_factor
Label (RO): Factor comun

Tiers:
  Easy   — Direct extraction & compute: a·b ± a·c = a·(b±c)
  Medium — Multi-term factoring, compute with known sums (a+b+c = k),
           factoring where the common factor appears as repeated coefficient
  Hard   — Substitution with given values, Gauss-style sums with common factor,
           expressions requiring rewriting before factoring

Usage:
    python manage.py load_exercises exercises.common_factor
    python manage.py load_exercises exercises.common_factor --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 6,  # "Înmulțirea numerelor naturale"
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Direct extraction & compute
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Factor comun: a·b + a·c",
        "category": "common_factor",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Factor comun: a·b + a·c",
            "type": "fill_blank",
            "question": "Evidențiind factorul comun, calculați:  ${a} \\cdot {b} + {a} \\cdot {c}$",
            "params": {
                "a": {"type": "randint", "min": 3, "max": 30},
                "b": {"type": "randint", "min": 10, "max": 99},
                "c": {"type": "randint", "min": 10, "max": 99},
            },
            "answer_expr": "{a} * {b} + {a} * {c}",
            "answer_input": "number",
            "hint": "Scoateți factorul comun ${a}$: ${a} \\cdot ({b} + {c})$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Factor comun: a·b − a·c",
        "category": "common_factor",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Factor comun: a·b − a·c",
            "type": "fill_blank",
            "question": "Evidențiind factorul comun, calculați:  ${a} \\cdot {b} - {a} \\cdot {c}$",
            "params": {
                "a": {"type": "randint", "min": 3, "max": 30},
                "c": {"type": "randint", "min": 10, "max": 49},
                "b": {"type": "randint", "min": 50, "max": 99},
            },
            "answer_expr": "{a} * {b} - {a} * {c}",
            "answer_input": "number",
            "hint": "Scoateți factorul comun ${a}$: ${a} \\cdot ({b} - {c})$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Factor comun la dreapta: b·a + c·a",
        "category": "common_factor",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Factor comun la dreapta: b·a + c·a",
            "type": "fill_blank",
            "question": "Evidențiind factorul comun, calculați:  ${b} \\cdot {a} + {c} \\cdot {a}$",
            "params": {
                "a": {"type": "randint", "min": 3, "max": 25},
                "b": {"type": "randint", "min": 10, "max": 50},
                "c": {"type": "randint", "min": 10, "max": 50},
            },
            "answer_expr": "{b} * {a} + {c} * {a}",
            "answer_input": "number",
            "hint": "Factorul comun este ${a}$: $({b} + {c}) \\cdot {a}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Scrieți ca produs: a·p − a·q",
        "category": "common_factor",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Scrieți ca produs: a·p − a·q",
            "type": "fill_blank",
            "question": "Urmând modelul $37 \\cdot 103 - 37 \\cdot 55 = 37 \\cdot (103 - 55) = 37 \\cdot 48 = 1776$, calculați:  ${a} \\cdot {p} - {a} \\cdot {q}$",
            "params": {
                "a": {"type": "randint", "min": 11, "max": 40},
                "q": {"type": "randint", "min": 10, "max": 50},
                "p": {"type": "randint", "min": 60, "max": 150},
            },
            "answer_expr": "{a} * {p} - {a} * {q}",
            "answer_input": "number",
            "hint": "Scoateți ${a}$ ca factor comun: ${a} \\cdot ({p} - {q})$.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Multi-term factoring, known sums
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Factor comun: trei termeni (+, +, −)",
        "category": "common_factor",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Factor comun: trei termeni (+, +, −)",
            "type": "fill_blank",
            "question": "Calculați folosind factorul comun:  ${a} \\cdot {b} + {a} \\cdot {c} - {a} \\cdot {d}$",
            "params": {
                "a": {"type": "randint", "min": 5, "max": 40},
                "b": {"type": "randint", "min": 20, "max": 80},
                "c": {"type": "randint", "min": 20, "max": 80},
                "d": {"type": "randint", "min": 5, "max": 30},
            },
            "answer_expr": "{a} * {b} + {a} * {c} - {a} * {d}",
            "answer_input": "number",
            "hint": "Scoateți ${a}$: ${a} \\cdot ({b} + {c} - {d})$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Sumă cunoscută: a+b+c = k, calculați n·(a+b+c)",
        "category": "common_factor",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Sumă cunoscută: n·a + n·b + n·c",
            "type": "fill_blank",
            "question": "Se știe că $a + b + c = {s}$. Calculați:  ${n} \\cdot a + {n} \\cdot b + {n} \\cdot c$",
            "params": {
                "s": {"type": "randint", "min": 5, "max": 30},
                "n": {"type": "randint", "min": 3, "max": 50},
            },
            "answer_expr": "{n} * {s}",
            "answer_input": "number",
            "hint": "Scoateți ${n}$ ca factor comun: ${n} \\cdot (a + b + c) = {n} \\cdot {s}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Sumă cunoscută cu constantă: n·(a+b+c) + k",
        "category": "common_factor",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Sumă cunoscută cu constantă",
            "type": "fill_blank",
            "question": "Se știe că $a + b + c = {s}$. Calculați:  ${n} \\cdot a + {n} \\cdot b + {n} \\cdot c + {k}$",
            "params": {
                "s": {"type": "randint", "min": 5, "max": 20},
                "n": {"type": "randint", "min": 3, "max": 30},
                "k": {"type": "randint", "min": 10, "max": 200},
            },
            "answer_expr": "{n} * {s} + {k}",
            "answer_input": "number",
            "hint": "Scoateți ${n}$: ${n} \\cdot (a + b + c) + {k} = {n} \\cdot {s} + {k}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Sumă cunoscută cu scădere: M − n·(a+b+c)",
        "category": "common_factor",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Sumă cunoscută cu scădere",
            "type": "fill_blank",
            "question": "Se știe că $a + b + c = {s}$. Calculați:  ${M} - ({n} \\cdot a + {n} \\cdot b + {n} \\cdot c)$",
            "params": {
                "s": {"type": "randint", "min": 5, "max": 15},
                "n": {"type": "randint", "min": 3, "max": 20},
                "M": {"type": "randint", "min": 500, "max": 2000},
            },
            "answer_expr": "{M} - {n} * {s}",
            "answer_input": "number",
            "hint": "Paranteza este ${n} \\cdot (a + b + c) = {n} \\cdot {s}$. Apoi scădeți din ${M}$.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Substitution, Gauss sums with common factor
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Substituție: a·b + a·c cu a și b+c date",
        "category": "common_factor",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Substituție: a·b + a·c cu a și b+c date",
            "type": "fill_blank",
            "question": "Calculați $a \\cdot b + a \\cdot c$ știind că $b + c = {bc}$ și $a = {a}$.",
            "params": {
                "a":  {"type": "randint", "min": 3, "max": 30},
                "bc": {"type": "randint", "min": 50, "max": 300},
            },
            "answer_expr": "{a} * {bc}",
            "answer_input": "number",
            "hint": "Scoateți $a$ ca factor comun: $a \\cdot (b + c) = {a} \\cdot {bc}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Substituție: a·b − a·c cu a și b−c date",
        "category": "common_factor",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Substituție: a·b − a·c cu a și b−c date",
            "type": "fill_blank",
            "question": "Calculați $a \\cdot b - a \\cdot c$ știind că $a = {a}$ și $b - c = {bc}$.",
            "params": {
                "a":  {"type": "randint", "min": 10, "max": 50},
                "bc": {"type": "randint", "min": 50, "max": 300},
            },
            "answer_expr": "{a} * {bc}",
            "answer_input": "number",
            "hint": "$a \\cdot b - a \\cdot c = a \\cdot (b - c) = {a} \\cdot {bc}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Substituție mixtă: x·a + x·b cu x și a+b date",
        "category": "common_factor",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Substituție mixtă: k·x + p·a + p·b",
            "type": "fill_blank",
            "question": "Dacă $x = {x}$ și $a + b = {ab}$, calculați:  ${k} \\cdot x + {p} \\cdot a + {p} \\cdot b$",
            "params": {
                "x":  {"type": "randint", "min": 3, "max": 20},
                "ab": {"type": "randint", "min": 5, "max": 30},
                "k":  {"type": "randint", "min": 3, "max": 15},
                "p":  {"type": "randint", "min": 3, "max": 15},
            },
            "answer_expr": "{k} * {x} + {p} * {ab}",
            "answer_input": "number",
            "hint": "Calculați ${k} \\cdot x = {k} \\cdot {x}$ și ${p} \\cdot (a + b) = {p} \\cdot {ab}$, apoi adunați.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Sumă Gauss cu factor comun: k + 2k + ... + nk",
        "category": "common_factor",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Sumă Gauss cu factor comun",
            "type": "fill_blank",
            "question": "Calculați, scoțând factorul comun:  ${k} + {k2} + {k3} + \\ldots + {last}$",
            "params": {
                "k":    {"type": "choice", "options": [5, 6, 8, 10, 12, 15, 20]},
                "n":    {"type": "randint", "min": 15, "max": 50},
                "k2":   {"type": "computed", "expr": "2 * {k}"},
                "k3":   {"type": "computed", "expr": "3 * {k}"},
                "last": {"type": "computed", "expr": "{n} * {k}"},
                "ans":  {"type": "computed", "expr": "{k} * {n} * ({n} + 1) // 2"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Scoateți ${k}$: ${k} \\cdot (1 + 2 + \\ldots + {n})$. Folosiți formula lui Gauss: $\\frac{{{n} \\cdot ({n}+1)}}{{2}}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Raport sume Gauss cu factor comun",
        "category": "common_factor",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Raport sume Gauss cu factor comun",
            "type": "fill_blank",
            "question": "Efectuați:  $({kbig} + {kbig_2} + \\ldots + {kbig_last}) : ({ksmall} + {ksmall_2} + \\ldots + {ksmall_last})$",
            "params": {
                "ksmall":      {"type": "randint", "min": 2, "max": 10},
                "ratio":       {"type": "randint", "min": 2, "max": 5},
                "n":           {"type": "randint", "min": 10, "max": 30},
                "kbig":        {"type": "computed", "expr": "{ksmall} * {ratio}"},
                "ksmall_2":    {"type": "computed", "expr": "2 * {ksmall}"},
                "ksmall_last": {"type": "computed", "expr": "{n} * {ksmall}"},
                "kbig_2":      {"type": "computed", "expr": "2 * {kbig}"},
                "kbig_last":   {"type": "computed", "expr": "{n} * {kbig}"},
            },
            "answer_expr": "{ratio}",
            "answer_input": "number",
            "hint": "Scoateți factorul comun din fiecare sumă: ${kbig} \\cdot (1+2+\\ldots+{n})$ la deîmpărțit, ${ksmall} \\cdot (1+2+\\ldots+{n})$ la împărțitor. Sumele Gauss se simplifică, rămâne ${kbig} : {ksmall}$.",
            "placeholder": "= ?",
        },
    },
]
