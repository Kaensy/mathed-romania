"""
Exercise data: power_last_digit
Topic 1.8 — Puterea cu exponent natural (sub-lesson B: ultima cifră, sume)

Category: power_last_digit
Label (RO): Ultima cifră a unei puteri

Tiers:
  Easy   — Direct computation possible:
             last digit of a^n for small n (n <= 4)
             stable-digit bases (0, 1, 5, 6 raised to any power)
  Medium — Cycle rule required but single term:
             last digit of a^n for large n, base ending in 2/3/7/8 (period 4)
             last digit of a^n for large n, base ending in 4/9 (period 2)
  Hard   — Compound last digit of sums/products:
             U(a^m + b^n + c^p)
             U(a^m · b^n)
             mixed-period combinations

Pedagogical focus: students learn to find last digit of u(a), identify the
cycle, divide the exponent by cycle length, use the remainder (mod) to pick
the right position in the cycle. This is the canonical Romanian Grade 5
"ultima cifră" drill.

Design notes:
  - Uses `computed` params to pre-calculate the last digit via modular
    arithmetic. Student must reason about it, but the answer is verified
    against the actual modular result.
  - For compound sums (Hard tier), we sum last digits modulo 10.
  - Bases are selected to land in each cycle class so we can target the
    specific rule being practiced.

Usage:
    python manage.py load_exercises exercises.power_last_digit
    python manage.py load_exercises exercises.power_last_digit --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 8,
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Direct computation or stable digit
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Ultima cifră: a^n pentru n mic",
        "category": "power_last_digit",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Ultima cifră: a^n pentru n mic",
            "type": "fill_blank",
            "question": "Determinați ultima cifră a numărului:  ${a}^{{{n}}}$",
            "params": {
                "a":   {"type": "randint", "min": 2, "max": 9},
                "n":   {"type": "randint", "min": 2, "max": 4},
                "ans": {"type": "computed", "expr": "({a} ** {n}) % 10"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Puterea este suficient de mică pentru a calcula direct: ${a}^{{{n}}}$.",
            "placeholder": "Ultima cifră = ?",
        },
    },
    {
        "name": "Ultima cifră: bază terminată în 0, 1, 5 sau 6",
        "category": "power_last_digit",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Ultima cifră: bază terminată în 0, 1, 5 sau 6",
            "type": "fill_blank",
            "question": "Determinați ultima cifră a numărului:  ${a}^{{{n}}}$",
            "params": {
                # Bases ending in 0, 1, 5 or 6 — last digit is stable.
                "last": {"type": "choice", "options": [0, 1, 5, 6]},
                # Pick a multi-digit base ending in that digit.
                "tens": {"type": "randint", "min": 1, "max": 9},
                "a":    {"type": "computed", "expr": "{tens} * 10 + {last}"},
                "n":    {"type": "choice", "options": [7, 15, 100, 2011, 2024]},
                "ans":  {"type": "computed", "expr": "{last} if {last} != 0 else 0"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Numerele terminate în $0$, $1$, $5$ sau $6$, ridicate la orice putere nenulă, se termină cu aceeași cifră.",
            "placeholder": "Ultima cifră = ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Cycle rule: period 4 or period 2
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Ultima cifră cu ciclu 4: bază terminată în 2, 3, 7 sau 8",
        "category": "power_last_digit",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Ultima cifră cu ciclu 4: bază terminată în 2, 3, 7 sau 8",
            "type": "fill_blank",
            "question": "Determinați ultima cifră a numărului:  ${a}^{{{n}}}$",
            "params": {
                # Bases ending in 2, 3, 7, 8 — period 4.
                "last": {"type": "choice", "options": [2, 3, 7, 8]},
                "tens": {"type": "randint", "min": 0, "max": 9},
                "a":    {"type": "computed", "expr": "{tens} * 10 + {last}"},
                # Choose exponents large enough to force cycle use.
                "n":    {"type": "randint", "min": 20, "max": 2024},
                "ans":  {"type": "computed", "expr": "({last} ** (((({n} - 1) % 4) + 1))) % 10"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Numerele terminate în ${last}$ au ultima cifră cu perioada $4$. Împărțiți exponentul ${n}$ la $4$. Restul ne arată poziția în ciclu: rest $1 \\to {last}^1$, rest $2 \\to {last}^2$, rest $3 \\to {last}^3$, rest $0 \\to {last}^4$.",
            "placeholder": "Ultima cifră = ?",
        },
    },
    {
        "name": "Ultima cifră cu ciclu 2: bază terminată în 4 sau 9",
        "category": "power_last_digit",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Ultima cifră cu ciclu 2: bază terminată în 4 sau 9",
            "type": "fill_blank",
            "question": "Determinați ultima cifră a numărului:  ${a}^{{{n}}}$",
            "params": {
                # Bases ending in 4 or 9 — period 2.
                # 4: odd exp -> 4, even exp -> 6
                # 9: odd exp -> 9, even exp -> 1
                "last": {"type": "choice", "options": [4, 9]},
                "tens": {"type": "randint", "min": 0, "max": 9},
                "a":    {"type": "computed", "expr": "{tens} * 10 + {last}"},
                "n":    {"type": "randint", "min": 20, "max": 2024},
                "ans":  {"type": "computed", "expr": "({last} if {n} % 2 == 1 else (6 if {last} == 4 else 1))"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Numerele terminate în ${last}$ au ultima cifră cu perioada $2$. Dacă exponentul ${n}$ este impar, ultima cifră este ${last}$. Dacă este par, devine $6$ (pentru $4$) sau $1$ (pentru $9$).",
            "placeholder": "Ultima cifră = ?",
        },
    },
    {
        "name": "Ultima cifră cu ciclu 4 — bază de 3 cifre",
        "category": "power_last_digit",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Ultima cifră cu ciclu 4 — bază de 3 cifre",
            "type": "fill_blank",
            "question": "Determinați ultima cifră a numărului:  ${a}^{{{n}}}$",
            "params": {
                # Larger base, still period 4.
                "last":  {"type": "choice", "options": [2, 3, 7, 8]},
                "hunds": {"type": "randint", "min": 1, "max": 9},
                "tens":  {"type": "randint", "min": 0, "max": 9},
                "a":     {"type": "computed", "expr": "{hunds} * 100 + {tens} * 10 + {last}"},
                "n":     {"type": "randint", "min": 100, "max": 2024},
                "ans":   {"type": "computed", "expr": "({last} ** (((({n} - 1) % 4) + 1))) % 10"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Conta doar ultima cifră a bazei, aici ${last}$. Împărțiți ${n}$ la $4$ și folosiți restul pentru a alege poziția în ciclu.",
            "placeholder": "Ultima cifră = ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Compound expressions (sums, products)
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Ultima cifră: sumă de două puteri",
        "category": "power_last_digit",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Ultima cifră: sumă de două puteri",
            "type": "fill_blank",
            "question": "Determinați ultima cifră a numărului:  ${a}^{{{m}}} + {b}^{{{n}}}$",
            "params": {
                "a":   {"type": "randint", "min": 12, "max": 99},
                "b":   {"type": "randint", "min": 12, "max": 99},
                "m":   {"type": "randint", "min": 50, "max": 2024},
                "n":   {"type": "randint", "min": 50, "max": 2024},
                # Compute last digit of each term via mod 10, then sum mod 10.
                "u_a": {"type": "computed", "expr": "pow({a}, {m}, 10)"},
                "u_b": {"type": "computed", "expr": "pow({b}, {n}, 10)"},
                "ans": {"type": "computed", "expr": "({u_a} + {u_b}) % 10"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Ultima cifră a unei sume este ultima cifră a sumei ultimelor cifre. Aflați separat ultima cifră a ${a}^{{{m}}}$ și a ${b}^{{{n}}}$, apoi adunați și luați ultima cifră.",
            "placeholder": "Ultima cifră = ?",
        },
    },
    {
        "name": "Ultima cifră: sumă de trei puteri cu același exponent",
        "category": "power_last_digit",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Ultima cifră: sumă de trei puteri cu același exponent",
            "type": "fill_blank",
            "question": "Determinați ultima cifră a numărului:  ${a}^{{{n}}} + {b}^{{{n}}} + {c}^{{{n}}}$",
            "params": {
                "a":   {"type": "randint", "min": 12, "max": 99},
                "b":   {"type": "randint", "min": 12, "max": 99},
                "c":   {"type": "randint", "min": 12, "max": 99},
                "n":   {"type": "randint", "min": 100, "max": 2024},
                "u_a": {"type": "computed", "expr": "pow({a}, {n}, 10)"},
                "u_b": {"type": "computed", "expr": "pow({b}, {n}, 10)"},
                "u_c": {"type": "computed", "expr": "pow({c}, {n}, 10)"},
                "ans": {"type": "computed", "expr": "({u_a} + {u_b} + {u_c}) % 10"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Aflați ultima cifră a fiecărei puteri folosind ultima cifră a bazei și exponentul ${n}$. Adunați cele trei ultime cifre și luați ultima cifră a rezultatului.",
            "placeholder": "Ultima cifră = ?",
        },
    },
    {
        "name": "Ultima cifră: produs de două puteri",
        "category": "power_last_digit",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Ultima cifră: produs de două puteri",
            "type": "fill_blank",
            "question": "Determinați ultima cifră a numărului:  ${a}^{{{m}}} \\cdot {b}^{{{n}}}$",
            "params": {
                "a":   {"type": "randint", "min": 12, "max": 99},
                "b":   {"type": "randint", "min": 12, "max": 99},
                "m":   {"type": "randint", "min": 50, "max": 2024},
                "n":   {"type": "randint", "min": 50, "max": 2024},
                "u_a": {"type": "computed", "expr": "pow({a}, {m}, 10)"},
                "u_b": {"type": "computed", "expr": "pow({b}, {n}, 10)"},
                "ans": {"type": "computed", "expr": "({u_a} * {u_b}) % 10"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Ultima cifră a unui produs este ultima cifră a produsului ultimelor cifre. Aflați separat ultima cifră a ${a}^{{{m}}}$ și a ${b}^{{{n}}}$, apoi înmulțiți și luați ultima cifră.",
            "placeholder": "Ultima cifră = ?",
        },
    },
]
