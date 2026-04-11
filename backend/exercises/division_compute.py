"""
Exercise data: division_compute
Topic 1.7 — Împărțirea

Category: division_compute
Label (RO): Calcul cu împărțiri

Tiers:
  Easy   — Direct exact division, division by round numbers (10, 100, 1000)
  Medium — Larger dividends, mixed expressions combining :, +, −, ·
  Hard   — Complex 4-operation expressions, Gauss sum ratios with
           common factor simplification

All templates guarantee exact division (zero remainder) by constructing
dividends as (divisor × quotient) from random quotients.

Usage:
    python manage.py load_exercises exercises.division_compute
    python manage.py load_exercises exercises.division_compute --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 7,  # "Împărțirea"
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Direct exact division
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Împărțire: 3-4 cifre : 1 cifră",
        "category": "division_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Împărțire: 3-4 cifre : 1 cifră",
            "type": "fill_blank",
            "question": "Calculați:  ${a} : {b}$",
            "params": {
                "b": {"type": "randint", "min": 2, "max": 9},
                "q": {"type": "randint", "min": 100, "max": 999},
                "a": {"type": "computed", "expr": "{b} * {q}"},
            },
            "answer_expr": "{q}",
            "answer_input": "number",
            "hint": "Împărțiți ${a}$ la ${b}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Împărțire: 3-4 cifre : 2 cifre",
        "category": "division_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Împărțire: 3-4 cifre : 2 cifre",
            "type": "fill_blank",
            "question": "Calculați:  ${a} : {b}$",
            "params": {
                "b": {"type": "randint", "min": 11, "max": 99},
                "q": {"type": "randint", "min": 10, "max": 99},
                "a": {"type": "computed", "expr": "{b} * {q}"},
            },
            "answer_expr": "{q}",
            "answer_input": "number",
            "hint": "Împărțiți ${a}$ la ${b}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Împărțire la 10, 100, 1000",
        "category": "division_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Împărțire la 10, 100, 1000",
            "type": "fill_blank",
            "question": "Calculați:  ${a} : {b}$",
            "params": {
                "k":  {"type": "randint", "min": 1, "max": 3},
                "b":  {"type": "computed", "expr": "10 ** {k}"},
                "q":  {"type": "randint", "min": 10, "max": 999},
                "a":  {"type": "computed", "expr": "{b} * {q}"},
            },
            "answer_expr": "{q}",
            "answer_input": "number",
            "hint": "Pentru a împărți la ${b}$, eliminați zerourile corespunzătoare de la sfârșitul numărului.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Împărțire: cât mic, divizor rotund",
        "category": "division_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Împărțire: cât mic, divizor rotund",
            "type": "fill_blank",
            "question": "Calculați:  ${a} : {b}$",
            "params": {
                "tens": {"type": "randint", "min": 2, "max": 9},
                "b":    {"type": "computed", "expr": "{tens} * 10"},
                "q":    {"type": "randint", "min": 5, "max": 50},
                "a":    {"type": "computed", "expr": "{b} * {q}"},
            },
            "answer_expr": "{q}",
            "answer_input": "number",
            "hint": "Împărțiți ${a}$ la ${b}$.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Larger numbers, mixed expressions
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Împărțire: numere mari (5-6 cifre : 3 cifre)",
        "category": "division_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Împărțire: numere mari (5-6 cifre : 3 cifre)",
            "type": "fill_blank",
            "question": "Calculați:  ${a} : {b}$",
            "params": {
                "b": {"type": "randint", "min": 100, "max": 999},
                "q": {"type": "randint", "min": 50, "max": 999},
                "a": {"type": "computed", "expr": "{b} * {q}"},
            },
            "answer_expr": "{q}",
            "answer_input": "number",
            "hint": "Efectuați împărțirea în coloană.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Expresie: a:b + c:d",
        "category": "division_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Expresie: a:b + c:d",
            "type": "fill_blank",
            "question": "Efectuați:  ${a} : {b} + {c} : {d}$",
            "params": {
                "b":  {"type": "randint", "min": 3, "max": 99},
                "q1": {"type": "randint", "min": 10, "max": 200},
                "a":  {"type": "computed", "expr": "{b} * {q1}"},
                "d":  {"type": "randint", "min": 3, "max": 99},
                "q2": {"type": "randint", "min": 10, "max": 200},
                "c":  {"type": "computed", "expr": "{d} * {q2}"},
            },
            "answer_expr": "{a} / {b} + {c} / {d}",
            "answer_input": "number",
            "hint": "Calculați fiecare împărțire separat, apoi adunați rezultatele.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Expresie: a:b − c:d",
        "category": "division_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Expresie: a:b − c:d",
            "type": "fill_blank",
            "question": "Efectuați:  ${a} : {b} - {c} : {d}$",
            "params": {
                "d":  {"type": "randint", "min": 3, "max": 50},
                "q2": {"type": "randint", "min": 5, "max": 50},
                "c":  {"type": "computed", "expr": "{d} * {q2}"},
                "b":  {"type": "randint", "min": 3, "max": 99},
                "q1": {"type": "randint", "min": 100, "max": 500},
                "a":  {"type": "computed", "expr": "{b} * {q1}"},
            },
            "answer_expr": "{a} / {b} - {c} / {d}",
            "answer_input": "number",
            "hint": "Calculați fiecare împărțire separat, apoi scădeți.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Expresie: a·b + c:d",
        "category": "division_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Expresie: a·b + c:d",
            "type": "fill_blank",
            "question": "Efectuați:  ${a} \\cdot {b} + {c} : {d}$",
            "params": {
                "a": {"type": "randint", "min": 10, "max": 200},
                "b": {"type": "randint", "min": 5, "max": 50},
                "d": {"type": "randint", "min": 3, "max": 99},
                "q": {"type": "randint", "min": 10, "max": 200},
                "c": {"type": "computed", "expr": "{d} * {q}"},
            },
            "answer_expr": "{a} * {b} + {c} / {d}",
            "answer_input": "number",
            "hint": "Efectuați înmulțirea și împărțirea (ordinul 2), apoi adunați.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Expresie: a·b − c:d",
        "category": "division_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Expresie: a·b − c:d",
            "type": "fill_blank",
            "question": "Efectuați:  ${a} \\cdot {b} - {c} : {d}$",
            "params": {
                "a": {"type": "randint", "min": 50, "max": 500},
                "b": {"type": "randint", "min": 5, "max": 50},
                "d": {"type": "randint", "min": 3, "max": 99},
                "q": {"type": "randint", "min": 5, "max": 50},
                "c": {"type": "computed", "expr": "{d} * {q}"},
            },
            "answer_expr": "{a} * {b} - {c} / {d}",
            "answer_input": "number",
            "hint": "Efectuați înmulțirea și împărțirea (ordinul 2), apoi scădeți.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Multi-operation expressions, Gauss ratios
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Expresie complexă: a·b + c·d + e:f",
        "category": "division_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Expresie complexă: a·b + c·d + e:f",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot {b} + {c} \\cdot {d} + {e} : {f}$",
            "params": {
                "a": {"type": "randint", "min": 50, "max": 500},
                "b": {"type": "randint", "min": 5, "max": 30},
                "c": {"type": "randint", "min": 10, "max": 100},
                "d": {"type": "randint", "min": 10, "max": 100},
                "f": {"type": "randint", "min": 10, "max": 99},
                "q": {"type": "randint", "min": 20, "max": 500},
                "e": {"type": "computed", "expr": "{f} * {q}"},
            },
            "answer_expr": "{a} * {b} + {c} * {d} + {e} / {f}",
            "answer_input": "number",
            "hint": "Efectuați cele trei operații de ordinul 2, apoi adunați rezultatele.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Expresie complexă: a·b + c:d − e:f",
        "category": "division_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Expresie complexă: a·b + c:d − e:f",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot {b} + {c} : {d} - {e} : {f}$",
            "params": {
                "a":  {"type": "randint", "min": 100, "max": 1000},
                "b":  {"type": "randint", "min": 10, "max": 100},
                "d":  {"type": "randint", "min": 10, "max": 99},
                "q1": {"type": "randint", "min": 50, "max": 500},
                "c":  {"type": "computed", "expr": "{d} * {q1}"},
                "f":  {"type": "randint", "min": 10, "max": 99},
                "q2": {"type": "randint", "min": 10, "max": 100},
                "e":  {"type": "computed", "expr": "{f} * {q2}"},
            },
            "answer_expr": "{a} * {b} + {c} / {d} - {e} / {f}",
            "answer_input": "number",
            "hint": "Efectuați toate operațiile de ordinul 2, apoi efectuați adunarea și scăderea de la stânga la dreapta.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Raport sume Gauss cu factor comun",
        "category": "division_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Raport sume Gauss cu factor comun",
            "type": "fill_blank",
            "question": "Efectuați:  $({kbig} + {kbig_2} + {kbig_3} + \\ldots + {kbig_last}) : ({ksmall} + {ksmall_2} + {ksmall_3} + \\ldots + {ksmall_last})$",
            "params": {
                "ksmall":      {"type": "randint", "min": 2, "max": 10},
                "ratio":       {"type": "randint", "min": 2, "max": 5},
                "n":           {"type": "randint", "min": 10, "max": 30},
                "kbig":        {"type": "computed", "expr": "{ksmall} * {ratio}"},
                "ksmall_2":    {"type": "computed", "expr": "2 * {ksmall}"},
                "ksmall_3":    {"type": "computed", "expr": "3 * {ksmall}"},
                "ksmall_last": {"type": "computed", "expr": "{n} * {ksmall}"},
                "kbig_2":      {"type": "computed", "expr": "2 * {kbig}"},
                "kbig_3":      {"type": "computed", "expr": "3 * {kbig}"},
                "kbig_last":   {"type": "computed", "expr": "{n} * {kbig}"},
            },
            "answer_expr": "{ratio}",
            "answer_input": "number",
            "hint": "Scoateți factorul comun din fiecare sumă: ${kbig} \\cdot (1+2+\\ldots+{n})$ la deîmpărțit, ${ksmall} \\cdot (1+2+\\ldots+{n})$ la împărțitor. Sumele Gauss se simplifică.",
            "placeholder": "= ?",
        },
    },
]
