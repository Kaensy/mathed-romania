"""
Exercise data: multiplication_compute
Topic 1.6 — Înmulțirea numerelor naturale: calcul și proprietăți

Category: multiplication_compute
Label (RO): Calcul cu înmulțiri

Tiers:
  Easy   — Direct 2-factor products (small & large), chain of 2-3 factors
  Medium — Mixed ops (·,+,−), parentheses, clever decomposition,
           commutativity/associativity tricks
  Hard   — Last digit of products, complex multi-operation expressions,
           factorial expressions

NOTE: The factorial templates require `from math import factorial` to be
added to exercise_engine.py's imports (bare eval needs it in scope).

Usage:
    python manage.py load_exercises exercises.multiplication_compute
    python manage.py load_exercises exercises.multiplication_compute --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 6  # "Înmulțirea numerelor naturale
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Direct computation
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Înmulțire: două numere de 2 cifre",
        "category": "multiplication_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Înmulțire: două numere de 2 cifre",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot {b}$",
            "params": {
                "a": {"type": "randint", "min": 11, "max": 99},
                "b": {"type": "randint", "min": 11, "max": 99},
            },
            "answer_expr": "{a} * {b}",
            "answer_input": "number",
            "hint": "Înmulțiți cele două numere.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Înmulțire: număr de 3-4 cifre × număr de 2-3 cifre",
        "category": "multiplication_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Înmulțire: număr de 3-4 cifre × număr de 2-3 cifre",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot {b}$",
            "params": {
                "a": {"type": "randint", "min": 100, "max": 9999},
                "b": {"type": "randint", "min": 11, "max": 999},
            },
            "answer_expr": "{a} * {b}",
            "answer_input": "number",
            "hint": "Înmulțiți cele două numere.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Înmulțire: număr rotund × număr",
        "category": "multiplication_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Înmulțire: număr rotund × număr",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot {b}$",
            "params": {
                "base": {"type": "randint", "min": 1, "max": 50},
                "a":    {"type": "computed", "expr": "{base} * 100"},
                "b":    {"type": "randint", "min": 11, "max": 999},
            },
            "answer_expr": "{a} * {b}",
            "answer_input": "number",
            "hint": "Înmulțiți ${base}$ cu ${b}$, apoi adăugați cele două zerouri.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Înmulțire: trei factori mici",
        "category": "multiplication_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Înmulțire: trei factori mici",
            "type": "fill_blank",
            "question": "Efectuați:  ${a} \\cdot {b} \\cdot {c}$",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 50},
                "b": {"type": "randint", "min": 2, "max": 50},
                "c": {"type": "randint", "min": 2, "max": 20},
            },
            "answer_expr": "{a} * {b} * {c}",
            "answer_input": "number",
            "hint": "Înmulțiți pe rând, de la stânga la dreapta.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Mixed operations, parentheses, clever tricks
    # ══════════════════════════════════════════════════════════════════════════

    # ── Mixed operations: a·b + c·d ──────────────────────────────────────────

    {
        "name": "Expresie: a·b + c·d",
        "category": "multiplication_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Expresie: a·b + c·d",
            "type": "fill_blank",
            "question": "Efectuați:  ${a} \\cdot {b} + {c} \\cdot {d}$",
            "params": {
                "a": {"type": "randint", "min": 10, "max": 500},
                "b": {"type": "randint", "min": 2, "max": 50},
                "c": {"type": "randint", "min": 10, "max": 500},
                "d": {"type": "randint", "min": 2, "max": 50},
            },
            "answer_expr": "{a} * {b} + {c} * {d}",
            "answer_input": "number",
            "hint": "Calculați mai întâi înmulțirile, apoi adunați rezultatele.",
            "placeholder": "= ?",
        },
    },

    # ── Mixed operations: a·b − c·d ──────────────────────────────────────────

    {
        "name": "Expresie: a·b − c·d",
        "category": "multiplication_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Expresie: a·b − c·d",
            "type": "fill_blank",
            "question": "Efectuați:  ${a} \\cdot {b} - {c} \\cdot {d}$",
            "params": {
                "c": {"type": "randint", "min": 10, "max": 200},
                "d": {"type": "randint", "min": 2, "max": 30},
                "a": {"type": "randint", "min": 200, "max": 1000},
                "b": {"type": "randint", "min": 5, "max": 50},
            },
            "answer_expr": "{a} * {b} - {c} * {d}",
            "answer_input": "number",
            "hint": "Calculați mai întâi fiecare înmulțire, apoi scădeți.",
            "placeholder": "= ?",
        },
    },

    # ── Parentheses: a·(b + c) ───────────────────────────────────────────────

    {
        "name": "Paranteze: a · (b + c)",
        "category": "multiplication_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Paranteze: a · (b + c)",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot ({b} + {c})$",
            "params": {
                "a": {"type": "randint", "min": 10, "max": 500},
                "b": {"type": "randint", "min": 10, "max": 999},
                "c": {"type": "randint", "min": 10, "max": 999},
            },
            "answer_expr": "{a} * ({b} + {c})",
            "answer_input": "number",
            "hint": "Calculați mai întâi paranteza: ${b} + {c}$, apoi înmulțiți cu ${a}$.",
            "placeholder": "= ?",
        },
    },

    # ── Parentheses: (a − b) · c ─────────────────────────────────────────────

    {
        "name": "Paranteze: (a − b) · c",
        "category": "multiplication_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Paranteze: (a − b) · c",
            "type": "fill_blank",
            "question": "Calculați:  $({a} - {b}) \\cdot {c}$",
            "params": {
                "b": {"type": "randint", "min": 10, "max": 500},
                "a": {"type": "randint", "min": 500, "max": 5000},
                "c": {"type": "randint", "min": 10, "max": 500},
            },
            "answer_expr": "({a} - {b}) * {c}",
            "answer_input": "number",
            "hint": "Calculați mai întâi paranteza: ${a} - {b}$, apoi înmulțiți cu ${c}$.",
            "placeholder": "= ?",
        },
    },

    # ── Parentheses: (a − b) · (c − d) ──────────────────────────────────────

    {
        "name": "Paranteze: (a − b) · (c − d)",
        "category": "multiplication_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Paranteze: (a − b) · (c − d)",
            "type": "fill_blank",
            "question": "Calculați:  $({a} - {b}) \\cdot ({c} - {d})$",
            "params": {
                "b": {"type": "randint", "min": 50, "max": 200},
                "a": {"type": "randint", "min": 200, "max": 500},
                "d": {"type": "randint", "min": 10, "max": 80},
                "c": {"type": "randint", "min": 80, "max": 200},
            },
            "answer_expr": "({a} - {b}) * ({c} - {d})",
            "answer_input": "number",
            "hint": "Calculați fiecare paranteză: ${a} - {b}$ și ${c} - {d}$, apoi înmulțiți rezultatele.",
            "placeholder": "= ?",
        },
    },

    # ── Clever decomposition: a · (10^k − 1) ─────────────────────────────────
    # Model: 6·999 = 6·(1000−1) = 6000−6 = 5994

    {
        "name": "Truc: a · (10^k − 1)",
        "category": "multiplication_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Truc: a · (10^k − 1)",
            "type": "fill_blank",
            "question": "Urmând modelul $6 \\cdot 999 = 6 \\cdot (1000-1) = 6000 - 6 = 5994$, calculați:  ${a} \\cdot {nines}$",
            "params": {
                "a":     {"type": "randint", "min": 3, "max": 12},
                "k":     {"type": "randint", "min": 2, "max": 4},
                "power": {"type": "computed", "expr": "10 ** {k}"},
                "nines": {"type": "computed", "expr": "10 ** {k} - 1"},
            },
            "answer_expr": "{a} * {nines}",
            "answer_input": "number",
            "hint": "Descompuneți: ${a} \\cdot {nines} = {a} \\cdot ({power} - 1) = {a} \\cdot {power} - {a}$.",
            "placeholder": "= ?",
        },
    },

    # ── Clever decomposition: a · (round + small) ────────────────────────────
    # Model: 8·402 = 8·(400+2) = 3200+16 = 3216

    {
        "name": "Truc: a · (rotund + mic)",
        "category": "multiplication_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Truc: a · (rotund + mic)",
            "type": "fill_blank",
            "question": "Urmând modelul $8 \\cdot 402 = 8 \\cdot (400+2) = 3200 + 16 = 3216$, calculați:  ${a} \\cdot {n}$",
            "params": {
                "a":        {"type": "randint", "min": 3, "max": 12},
                "hundreds": {"type": "randint", "min": 1, "max": 9},
                "small":    {"type": "randint", "min": 1, "max": 9},
                "base":     {"type": "computed", "expr": "{hundreds} * 100"},
                "n":        {"type": "computed", "expr": "{base} + {small}"},
            },
            "answer_expr": "{a} * {n}",
            "answer_input": "number",
            "hint": "Descompuneți: ${a} \\cdot {n} = {a} \\cdot ({base} + {small}) = {a} \\cdot {base} + {a} \\cdot {small}$.",
            "placeholder": "= ?",
        },
    },

    # ── Commutativity/associativity: rearrange to simplify ───────────────────
    # Ex 14 style: 5·43·2 = (5·2)·43 = 10·43 = 430

    {
        "name": "Asociativitate: factori cu produs 10",
        "category": "multiplication_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Asociativitate: factori cu produs 10",
            "type": "fill_blank",
            "question": "Folosind asociativitatea și comutativitatea, calculați:  ${a} \\cdot {mid} \\cdot {b}$",
            "params": {
                "a":   {"type": "choice", "options": [2, 5]},
                "b":   {"type": "computed", "expr": "10 // {a}"},
                "mid": {"type": "randint", "min": 11, "max": 999},
            },
            "answer_expr": "{a} * {mid} * {b}",
            "answer_input": "number",
            "hint": "Observați: ${a} \\cdot {b} = 10$. Deci rezultatul este $10 \\cdot {mid}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Asociativitate: factori cu produs 100",
        "category": "multiplication_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Asociativitate: factori cu produs 100",
            "type": "fill_blank",
            "question": "Folosind asociativitatea și comutativitatea, calculați:  ${a} \\cdot {mid} \\cdot {b}$",
            "params": {
                "a":   {"type": "choice", "options": [4, 5, 20, 25, 50]},
                "b":   {"type": "computed", "expr": "100 // {a}"},
                "mid": {"type": "randint", "min": 11, "max": 200},
            },
            "answer_expr": "{a} * {mid} * {b}",
            "answer_input": "number",
            "hint": "Observați: ${a} \\cdot {b} = 100$. Deci rezultatul este $100 \\cdot {mid}$.",
            "placeholder": "= ?",
        },
    },

    # ── Medium: 3-operation expression ────────────────────────────────────────

    {
        "name": "Expresie: a·b + c·d − e·f",
        "category": "multiplication_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Expresie: a·b + c·d − e·f",
            "type": "fill_blank",
            "question": "Efectuați:  ${a} \\cdot {b} + {c} \\cdot {d} - {e} \\cdot {f}$",
            "params": {
                "a": {"type": "randint", "min": 10, "max": 200},
                "b": {"type": "randint", "min": 2, "max": 30},
                "c": {"type": "randint", "min": 10, "max": 200},
                "d": {"type": "randint", "min": 2, "max": 30},
                "e": {"type": "randint", "min": 2, "max": 50},
                "f": {"type": "randint", "min": 2, "max": 20},
            },
            "answer_expr": "{a} * {b} + {c} * {d} - {e} * {f}",
            "answer_input": "number",
            "hint": "Calculați mai întâi fiecare înmulțire, apoi efectuați adunarea și scăderea.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Last digit, complex expressions, factorial expressions
    # ══════════════════════════════════════════════════════════════════════════

    # ── Last digit of a product ──────────────────────────────────────────────

    {
        "name": "Ultima cifră: produs de 3 numere",
        "category": "multiplication_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Ultima cifră: produs de 3 numere",
            "type": "fill_blank",
            "question": "Determinați ultima cifră a produsului:  $P = {a} \\cdot {b} \\cdot {c}$",
            "params": {
                "a":   {"type": "randint", "min": 100, "max": 9999},
                "b":   {"type": "randint", "min": 100, "max": 9999},
                "c":   {"type": "randint", "min": 100, "max": 9999},
                "ans": {"type": "computed", "expr": "({a} * {b} * {c}) % 10"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Nu trebuie să calculați tot produsul! Înmulțiți doar cifrele unităților celor trei numere, apoi luați ultima cifră.",
            "placeholder": "Ultima cifră = ?",
        },
    },
    {
        "name": "Ultima cifră: produs de 5 numere",
        "category": "multiplication_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Ultima cifră: produs de 5 numere",
            "type": "fill_blank",
            "question": "Determinați ultima cifră a produsului:  $P = {a} \\cdot {b} \\cdot {c} \\cdot {d} \\cdot {e}$",
            "params": {
                "a":   {"type": "randint", "min": 10, "max": 999},
                "b":   {"type": "randint", "min": 10, "max": 999},
                "c":   {"type": "randint", "min": 10, "max": 999},
                "d":   {"type": "randint", "min": 10, "max": 999},
                "e":   {"type": "randint", "min": 10, "max": 999},
                "ans": {"type": "computed", "expr": "({a} * {b} * {c} * {d} * {e}) % 10"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Înmulțiți pe rând doar cifrele unităților, păstrând la fiecare pas doar ultima cifră a rezultatului parțial.",
            "placeholder": "Ultima cifră = ?",
        },
    },

    # ── Complex multi-operation expressions ───────────────────────────────────

    {
        "name": "Expresie complexă: a·b − c",
        "category": "multiplication_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Expresie complexă: a·b − c",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot {b} - {c}$",
            "params": {
                "a": {"type": "randint", "min": 100, "max": 9999},
                "b": {"type": "randint", "min": 100, "max": 999},
                "c": {"type": "randint", "min": 1000, "max": 99999},
            },
            "answer_expr": "{a} * {b} - {c}",
            "answer_input": "number",
            "hint": "Calculați mai întâi produsul ${a} \\cdot {b}$, apoi scădeți ${c}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Expresie complexă: a·b + c·d − e·f (numere mari)",
        "category": "multiplication_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Expresie complexă: a·b + c·d − e·f (numere mari)",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot {b} + {c} \\cdot {d} - {e} \\cdot {f}$",
            "params": {
                "a": {"type": "randint", "min": 100, "max": 5000},
                "b": {"type": "randint", "min": 10, "max": 100},
                "c": {"type": "randint", "min": 100, "max": 5000},
                "d": {"type": "randint", "min": 10, "max": 100},
                "e": {"type": "randint", "min": 10, "max": 500},
                "f": {"type": "randint", "min": 10, "max": 50},
            },
            "answer_expr": "{a} * {b} + {c} * {d} - {e} * {f}",
            "answer_input": "number",
            "hint": "Calculați cele trei produse individual, apoi combinați rezultatele.",
            "placeholder": "= ?",
        },
    },

    # ── Comparisons ──────────────────────────────────────────────────────────

    {
        "name": "Comparare produse: a·b vs c·d",
        "category": "multiplication_compute",
        "difficulty": "hard",
        "exercise_type": "comparison",
        "template": {
            "title": "Comparare produse: a·b vs c·d",
            "type": "comparison",
            "question": "Comparați:",
            "params": {
                "a": {"type": "randint", "min": 10, "max": 999},
                "b": {"type": "randint", "min": 10, "max": 999},
                "c": {"type": "randint", "min": 10, "max": 999},
                "d": {"type": "randint", "min": 10, "max": 999},
            },
            "left": "{a} * {b}",
            "right": "{c} * {d}",
        },
    },

    # ── Factorial expressions ────────────────────────────────────────────────
    # REQUIRES: `from math import factorial` in exercise_engine.py

    {
        "name": "Factorial: calculați n!",
        "category": "multiplication_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Factorial: calculați n!",
            "type": "fill_blank",
            "question": "Știind că $n! = 1 \\cdot 2 \\cdot 3 \\cdot \\ldots \\cdot n$ (și $0! = 1$), calculați:  ${n}!$",
            "params": {
                "n":   {"type": "randint", "min": 4, "max": 8},
                "ans": {"type": "computed", "expr": "factorial({n})"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Înmulțiți: $1 \\cdot 2 \\cdot 3 \\cdot \\ldots \\cdot {n}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Factorial: expresie n!·a − m!·b",
        "category": "multiplication_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Factorial: expresie n!·a − m!·b",
            "type": "fill_blank",
            "question": "Calculați:  ${n}! \\cdot {a} - {m}! \\cdot {b}$",
            "params": {
                "n":     {"type": "randint", "min": 5, "max": 7},
                "m":     {"type": "computed", "expr": "{n} - 1"},
                "a":     {"type": "randint", "min": 5, "max": 20},
                "b":     {"type": "randint", "min": 5, "max": 20},
                "nfact": {"type": "computed", "expr": "factorial({n})"},
                "mfact": {"type": "computed", "expr": "factorial({m})"},
                "ans":   {"type": "computed", "expr": "{nfact} * {a} - {mfact} * {b}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Mai întâi calculați ${n}! = {nfact}$ și ${m}! = {mfact}$, apoi efectuați: ${nfact} \\cdot {a} - {mfact} \\cdot {b}$.",
            "placeholder": "= ?",
        },
    },
]
