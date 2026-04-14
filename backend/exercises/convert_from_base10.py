"""
Exercise data: convert_from_base10
Topic 1.9 — Baze de numerație: scrierea în baza 10 și baza 2

Category: convert_from_base10
Label (RO): Conversie din baza 10

Tiers:
  Easy   — Recompose from base-10 expanded form:
             3·10³ + 9·10² + 2 → 3902
           The inverse of Easy-tier convert_to_base10.
  Medium — Base 10 → base 2 via successive division:
             22 → 10110₍₂₎, 39 → 100111₍₂₎, 75 → 1001011₍₂₎
  Hard   — Base 10 → bases 3-9 via successive division:
             43 → 1121₍₃₎, 67 → 2111₍₃₎, 200 → 242₍₈₎

Design notes:
  - Answer format is a single fill_blank where student types the digit
    string of the result in the target base. SymPy/grade_expression
    will fail on non-decimal inputs, so answer_input is "number" and the
    correct_expr evaluates to the base-10 integer whose digit string
    equals the target representation (e.g., "10110" = 10110 as a number).
  - This is a clever hack: "write 22 in base 2" → expected answer 10110.
    SymPy grades 10110 == 10110 which is exactly what we want.
  - Computed `ans` param uses Python's built-in int-to-base via a small
    expression: we generate the digits mathematically and assemble them.

Usage:
    python manage.py load_exercises exercises.convert_from_base10
    python manage.py load_exercises exercises.convert_from_base10 --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 9,
}

# ─── Helper expression builders (used inline in computed exprs) ────────────────
#
# For a 4-digit base-b representation of n: digits are
#   d3 = n // b^3
#   d2 = (n // b^2) % b
#   d1 = (n // b)   % b
#   d0 = n % b
# and the displayed answer is d3*1000 + d2*100 + d1*10 + d0 (as a decimal
# number whose digits MATCH the base-b representation).
#
# We build these inline in the `computed` params below.

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Recompose from base-10 expanded form
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Recompunere baza 10: 3 cifre",
        "category": "convert_from_base10",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Recompunere baza 10: 3 cifre",
            "type": "fill_blank",
            "question": "Scrieți numărul natural care are descompunerea:  ${a} \\cdot 10^2 + {b} \\cdot 10 + {c}$",
            "params": {
                "a":   {"type": "randint", "min": 1, "max": 9},
                "b":   {"type": "randint", "min": 0, "max": 9},
                "c":   {"type": "randint", "min": 0, "max": 9},
                "ans": {"type": "computed", "expr": "{a} * 100 + {b} * 10 + {c}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Puterile lui 10: $10^2 = 100$, $10 = 10$, $1$. Înmulțiți fiecare cifră cu puterea corespunzătoare și adunați.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Recompunere baza 10: 4 cifre",
        "category": "convert_from_base10",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Recompunere baza 10: 4 cifre",
            "type": "fill_blank",
            "question": "Scrieți numărul natural care are descompunerea:  ${a} \\cdot 10^3 + {b} \\cdot 10^2 + {c} \\cdot 10 + {d}$",
            "params": {
                "a":   {"type": "randint", "min": 1, "max": 9},
                "b":   {"type": "randint", "min": 0, "max": 9},
                "c":   {"type": "randint", "min": 0, "max": 9},
                "d":   {"type": "randint", "min": 0, "max": 9},
                "ans": {"type": "computed", "expr": "{a} * 1000 + {b} * 100 + {c} * 10 + {d}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Puterile lui 10: $10^3 = 1000$, $10^2 = 100$, $10 = 10$, $1$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Recompunere baza 10: cu zerouri și semne",
        "category": "convert_from_base10",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Recompunere baza 10: cu zerouri și semne",
            "type": "fill_blank",
            "question": "Scrieți numărul natural care are descompunerea:  ${a} \\cdot 10^5 + {b} \\cdot 10^3 - {c} \\cdot 10^2 + {d}$",
            "params": {
                # Designed to mirror Ex 2d: 6·10^5 + 8·10^3 - 8·10^2 + 9.
                # Guarantee non-negative by keeping c small.
                "a":   {"type": "randint", "min": 1, "max": 9},
                "b":   {"type": "randint", "min": 1, "max": 9},
                "c":   {"type": "randint", "min": 1, "max": 9},
                "d":   {"type": "randint", "min": 0, "max": 9},
                "ans": {"type": "computed", "expr": "{a} * 100000 + {b} * 1000 - {c} * 100 + {d}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Calculați fiecare termen, apoi adunați/scădeți. Puterile lui 10 cresc de la dreapta la stânga.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Base 10 → base 2
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Conversie baza 10 → baza 2: n mic (≤ 31)",
        "category": "convert_from_base10",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Conversie baza 10 → baza 2: n mic (≤ 31)",
            "type": "fill_blank",
            "question": "Scrieți în baza 2 numărul ${n}$.",
            "params": {
                # n in [8, 31] → 4 or 5 binary digits.
                "n":   {"type": "randint", "min": 8, "max": 31},
                # Binary digits d4..d0, assembled as decimal integer.
                "d4":  {"type": "computed", "expr": "({n} // 16) % 2"},
                "d3":  {"type": "computed", "expr": "({n} // 8) % 2"},
                "d2":  {"type": "computed", "expr": "({n} // 4) % 2"},
                "d1":  {"type": "computed", "expr": "({n} // 2) % 2"},
                "d0":  {"type": "computed", "expr": "{n} % 2"},
                "ans": {"type": "computed", "expr": "{d4} * 10000 + {d3} * 1000 + {d2} * 100 + {d1} * 10 + {d0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Împărțiți succesiv la $2$ și notați resturile de jos în sus. Răspunsul se scrie ca șir de $0$-uri și $1$-uri (fără indice).",
            "placeholder": "ex: 10110",
        },
    },
    {
        "name": "Conversie baza 10 → baza 2: n mediu (≤ 127)",
        "category": "convert_from_base10",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Conversie baza 10 → baza 2: n mediu (≤ 127)",
            "type": "fill_blank",
            "question": "Scrieți în baza 2 numărul ${n}$.",
            "params": {
                "n":   {"type": "randint", "min": 32, "max": 127},
                "d6":  {"type": "computed", "expr": "({n} // 64) % 2"},
                "d5":  {"type": "computed", "expr": "({n} // 32) % 2"},
                "d4":  {"type": "computed", "expr": "({n} // 16) % 2"},
                "d3":  {"type": "computed", "expr": "({n} // 8) % 2"},
                "d2":  {"type": "computed", "expr": "({n} // 4) % 2"},
                "d1":  {"type": "computed", "expr": "({n} // 2) % 2"},
                "d0":  {"type": "computed", "expr": "{n} % 2"},
                "ans": {"type": "computed", "expr": "{d6} * 1000000 + {d5} * 100000 + {d4} * 10000 + {d3} * 1000 + {d2} * 100 + {d1} * 10 + {d0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Împărțiri succesive la $2$. Resturile (de jos în sus) formează scrierea în baza $2$. Răspunsul se introduce ca șir de cifre.",
            "placeholder": "ex: 1011010",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Base 10 → bases 3-9
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Conversie baza 10 → baza 3",
        "category": "convert_from_base10",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Conversie baza 10 → baza 3",
            "type": "fill_blank",
            "question": "Scrieți în baza 3 numărul ${n}$.",
            "params": {
                # n in [27, 242] → 4 or 5 ternary digits.
                "n":   {"type": "randint", "min": 27, "max": 242},
                "d4":  {"type": "computed", "expr": "({n} // 81) % 3"},
                "d3":  {"type": "computed", "expr": "({n} // 27) % 3"},
                "d2":  {"type": "computed", "expr": "({n} // 9) % 3"},
                "d1":  {"type": "computed", "expr": "({n} // 3) % 3"},
                "d0":  {"type": "computed", "expr": "{n} % 3"},
                "ans": {"type": "computed", "expr": "{d4} * 10000 + {d3} * 1000 + {d2} * 100 + {d1} * 10 + {d0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Împărțiți succesiv la $3$, notând resturile. Resturile citite de jos în sus dau scrierea în baza $3$. Cifrele pot fi doar $0$, $1$ sau $2$.",
            "placeholder": "ex: 1121",
        },
    },
    {
        "name": "Conversie baza 10 → baza 5",
        "category": "convert_from_base10",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Conversie baza 10 → baza 5",
            "type": "fill_blank",
            "question": "Scrieți în baza 5 numărul ${n}$.",
            "params": {
                # n in [125, 624] → 4 cifre în baza 5.
                "n":   {"type": "randint", "min": 125, "max": 624},
                "d3":  {"type": "computed", "expr": "({n} // 125) % 5"},
                "d2":  {"type": "computed", "expr": "({n} // 25) % 5"},
                "d1":  {"type": "computed", "expr": "({n} // 5) % 5"},
                "d0":  {"type": "computed", "expr": "{n} % 5"},
                "ans": {"type": "computed", "expr": "{d3} * 1000 + {d2} * 100 + {d1} * 10 + {d0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Împărțiți succesiv la $5$. Cifrele în baza $5$ pot fi $0, 1, 2, 3, 4$.",
            "placeholder": "ex: 2134",
        },
    },
    {
        "name": "Conversie baza 10 → baza 7",
        "category": "convert_from_base10",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Conversie baza 10 → baza 7",
            "type": "fill_blank",
            "question": "Scrieți în baza 7 numărul ${n}$.",
            "params": {
                # n in [343, 2400] → 4 cifre în baza 7.
                "n":   {"type": "randint", "min": 343, "max": 2400},
                "d3":  {"type": "computed", "expr": "({n} // 343) % 7"},
                "d2":  {"type": "computed", "expr": "({n} // 49) % 7"},
                "d1":  {"type": "computed", "expr": "({n} // 7) % 7"},
                "d0":  {"type": "computed", "expr": "{n} % 7"},
                "ans": {"type": "computed", "expr": "{d3} * 1000 + {d2} * 100 + {d1} * 10 + {d0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Împărțiți succesiv la $7$. Cifrele în baza $7$ pot fi $0, 1, \\ldots, 6$.",
            "placeholder": "ex: 1234",
        },
    },
    {
        "name": "Conversie baza 10 → baza 9",
        "category": "convert_from_base10",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Conversie baza 10 → baza 9",
            "type": "fill_blank",
            "question": "Scrieți în baza 9 numărul ${n}$.",
            "params": {
                # n in [729, 6560] → 4 cifre în baza 9.
                "n":   {"type": "randint", "min": 729, "max": 6560},
                "d3":  {"type": "computed", "expr": "({n} // 729) % 9"},
                "d2":  {"type": "computed", "expr": "({n} // 81) % 9"},
                "d1":  {"type": "computed", "expr": "({n} // 9) % 9"},
                "d0":  {"type": "computed", "expr": "{n} % 9"},
                "ans": {"type": "computed", "expr": "{d3} * 1000 + {d2} * 100 + {d1} * 10 + {d0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Împărțiți succesiv la $9$. Cifrele în baza $9$ pot fi $0, 1, \\ldots, 8$.",
            "placeholder": "ex: 1234",
        },
    },
]
