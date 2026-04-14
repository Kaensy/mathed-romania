"""
Exercise data: power_rules_simplify
Topic 1.8 — Puterea cu exponent natural (sub-lesson A: definiție și reguli)

Category: power_rules_simplify
Label (RO): Scriere ca o singură putere

Tiers:
  Easy   — Single application of rules 1-3:
             (1) a^m · a^n = a^(m+n)
             (2) a^m : a^n = a^(m-n)     for m >= n
             (3) (a^m)^n   = a^(m·n)
  Medium — Rules 4-5 and their inverses, plus 2-rule chains:
             (4) (a·b)^n = a^n · b^n       and its inverse
             (5) (a:b)^n = a^n : b^n       and its inverse (a divisible by b)
             triple-nested rule 3
             rule 3 + rule 1 combined
  Hard   — Rebasing: recognize different-looking bases as powers of a common
           base (4 = 2^2, 8 = 2^3, 25 = 5^2, 125 = 5^3, etc.), then combine.
           Multi-factor inverse of rule 4.

Design notes:
  - All `answer_expr` values evaluate to a single `base^exponent` form using
    Python `**`. SymPy grades any equivalent expression as correct, so
    students may submit a^m · a^n, a^(m+n), or the raw numeric value.
  - For divisions we ensure m >= n so the exponent stays a natural number.
  - For rule 5 (a:b)^n we use computed params to ensure a = k·b, so the
    quotient is always a natural number.

Usage:
    python manage.py load_exercises exercises.power_rules_simplify
    python manage.py load_exercises exercises.power_rules_simplify --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 8,
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Single rule application (rules 1, 2, 3)
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Regula 1: a^m · a^n",
        "category": "power_rules_simplify",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Regula 1: a^m · a^n",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere:  ${a}^{{{m}}} \\cdot {a}^{{{n}}}$",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 20},
                "m": {"type": "randint", "min": 3, "max": 30},
                "n": {"type": "randint", "min": 3, "max": 30},
            },
            "answer_expr": "{a}**({m} + {n})",
            "answer_input": "expression",
            "hint": "$a^m \\cdot a^n = a^{{m+n}}$ — se păstrează baza și se adună exponenții.",
            "placeholder": "ex: 2^40",
        },
    },
    {
        "name": "Regula 2: a^m : a^n",
        "category": "power_rules_simplify",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Regula 2: a^m : a^n",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere:  ${a}^{{{m}}} : {a}^{{{n}}}$",
            "params": {
                "a":    {"type": "randint", "min": 2, "max": 20},
                "n":    {"type": "randint", "min": 3, "max": 25},
                "diff": {"type": "randint", "min": 2, "max": 30},
                "m":    {"type": "computed", "expr": "{n} + {diff}"},
            },
            "answer_expr": "{a}**{diff}",
            "answer_input": "expression",
            "hint": "$a^m : a^n = a^{{m-n}}$ — se păstrează baza și se scad exponenții.",
            "placeholder": "ex: 2^10",
        },
    },
    {
        "name": "Regula 3: (a^m)^n",
        "category": "power_rules_simplify",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Regula 3: (a^m)^n",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere:  $({a}^{{{m}}})^{{{n}}}$",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 15},
                "m": {"type": "randint", "min": 2, "max": 15},
                "n": {"type": "randint", "min": 2, "max": 15},
            },
            "answer_expr": "{a}**({m} * {n})",
            "answer_input": "expression",
            "hint": "$(a^m)^n = a^{{m \\cdot n}}$ — se păstrează baza și se înmulțesc exponenții.",
            "placeholder": "ex: 2^20",
        },
    },
    {
        "name": "Regula 1 cu trei factori: a^k · a^m · a^n",
        "category": "power_rules_simplify",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Regula 1 cu trei factori: a^k · a^m · a^n",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere:  ${a}^{{{k}}} \\cdot {a}^{{{m}}} \\cdot {a}^{{{n}}}$",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 15},
                "k": {"type": "randint", "min": 2, "max": 15},
                "m": {"type": "randint", "min": 2, "max": 15},
                "n": {"type": "randint", "min": 2, "max": 15},
            },
            "answer_expr": "{a}**({k} + {m} + {n})",
            "answer_input": "expression",
            "hint": "Aceeași regulă $a^m \\cdot a^n = a^{{m+n}}$ se aplică și pentru trei factori. Adunați toți exponenții.",
            "placeholder": "ex: 2^25",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Rules 4, 5 and their inverses; 2-rule chains
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Regula 4: (a · b)^n",
        "category": "power_rules_simplify",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Regula 4: (a · b)^n",
            "type": "fill_blank",
            "question": "Scrieți ca produs de două puteri:  $({a} \\cdot {b})^{{{n}}}$",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 10},
                "b": {"type": "randint", "min": 2, "max": 10},
                "n": {"type": "randint", "min": 3, "max": 25},
            },
            "answer_expr": "{a}**{n} * {b}**{n}",
            "answer_input": "expression",
            "hint": "$(a \\cdot b)^n = a^n \\cdot b^n$ — exponentul se distribuie fiecărui factor.",
            "placeholder": "ex: 2^14 · 7^14",
        },
    },
    {
        "name": "Regula 5: (a : b)^n cu a divizibil cu b",
        "category": "power_rules_simplify",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Regula 5: (a : b)^n",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere:  $({a} : {b})^{{{n}}}$",
            "params": {
                "b": {"type": "randint", "min": 2, "max": 6},
                "k": {"type": "randint", "min": 2, "max": 8},
                "a": {"type": "computed", "expr": "{b} * {k}"},
                "n": {"type": "randint", "min": 5, "max": 30},
            },
            "answer_expr": "{k}**{n}",
            "answer_input": "expression",
            "hint": "$(a : b)^n = a^n : b^n$. Dar mai simplu: calculați întâi ${a} : {b} = {k}$, apoi ridicați la puterea ${n}$.",
            "placeholder": "ex: 4^21",
        },
    },
    {
        "name": "Invers regula 4: a^n · b^n",
        "category": "power_rules_simplify",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Invers regula 4: a^n · b^n",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere:  ${a}^{{{n}}} \\cdot {b}^{{{n}}}$",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 10},
                "b": {"type": "randint", "min": 2, "max": 10},
                "n": {"type": "randint", "min": 5, "max": 30},
            },
            "answer_expr": "({a} * {b})**{n}",
            "answer_input": "expression",
            "hint": "Când două puteri au același exponent: $a^n \\cdot b^n = (a \\cdot b)^n$.",
            "placeholder": "ex: 6^13",
        },
    },
    {
        "name": "Invers regula 5: a^n : b^n cu a divizibil cu b",
        "category": "power_rules_simplify",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Invers regula 5: a^n : b^n",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere:  ${a}^{{{n}}} : {b}^{{{n}}}$",
            "params": {
                "b": {"type": "randint", "min": 2, "max": 6},
                "k": {"type": "randint", "min": 2, "max": 8},
                "a": {"type": "computed", "expr": "{b} * {k}"},
                "n": {"type": "randint", "min": 5, "max": 30},
            },
            "answer_expr": "{k}**{n}",
            "answer_input": "expression",
            "hint": "Când două puteri au același exponent: $a^n : b^n = (a : b)^n$. Calculați ${a} : {b} = {k}$.",
            "placeholder": "ex: 4^24",
        },
    },
    {
        "name": "Regula 3 triplu imbricată: [(a^m)^n]^p",
        "category": "power_rules_simplify",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Regula 3 triplu imbricată: [(a^m)^n]^p",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere:  $[({a}^{{{m}}})^{{{n}}}]^{{{p}}}$",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 12},
                "m": {"type": "randint", "min": 2, "max": 6},
                "n": {"type": "randint", "min": 2, "max": 6},
                "p": {"type": "randint", "min": 2, "max": 6},
            },
            "answer_expr": "{a}**({m} * {n} * {p})",
            "answer_input": "expression",
            "hint": "Aplicați regula $(a^m)^n = a^{{m \\cdot n}}$ de două ori. Exponentul final este ${m} \\cdot {n} \\cdot {p}$.",
            "placeholder": "ex: 2^48",
        },
    },
    {
        "name": "Lanț cu două reguli: (a^m)^n · a^k",
        "category": "power_rules_simplify",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Lanț cu două reguli: (a^m)^n · a^k",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere:  $({a}^{{{m}}})^{{{n}}} \\cdot {a}^{{{k}}}$",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 12},
                "m": {"type": "randint", "min": 2, "max": 8},
                "n": {"type": "randint", "min": 2, "max": 8},
                "k": {"type": "randint", "min": 2, "max": 15},
            },
            "answer_expr": "{a}**({m} * {n} + {k})",
            "answer_input": "expression",
            "hint": "Aplicați mai întâi regula 3: $({a}^{{{m}}})^{{{n}}} = {a}^{{{m} \\cdot {n}}}$. Apoi regula 1 pentru a combina cu ${a}^{{{k}}}$.",
            "placeholder": "ex: 2^17",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Rebasing and multi-factor inverses
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Rebazare în puteri ale lui 2: 4^a · 8^b · 16^c",
        "category": "power_rules_simplify",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Rebazare în puteri ale lui 2: 4^a · 8^b · 16^c",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere a lui $2$:  $4^{{{a}}} \\cdot 8^{{{b}}} \\cdot 16^{{{c}}}$",
            "params": {
                "a": {"type": "randint", "min": 5, "max": 20},
                "b": {"type": "randint", "min": 5, "max": 20},
                "c": {"type": "randint", "min": 5, "max": 20},
            },
            "answer_expr": "2**(2 * {a} + 3 * {b} + 4 * {c})",
            "answer_input": "expression",
            "hint": "Rescrieți fiecare bază ca putere a lui $2$:  $4 = 2^2$, $8 = 2^3$, $16 = 2^4$. Apoi aplicați regula $(2^p)^q = 2^{{p \\cdot q}}$ și adunați exponenții.",
            "placeholder": "ex: 2^128",
        },
    },
    {
        "name": "Rebazare în puteri ale lui 5: 25^a · 125^b : 5^c",
        "category": "power_rules_simplify",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Rebazare în puteri ale lui 5: 25^a · 125^b : 5^c",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere a lui $5$:  $25^{{{a}}} \\cdot 125^{{{b}}} : 5^{{{c}}}$",
            "params": {
                # Ensure 2a + 3b - c >= 0. With a >= 5, b >= 3: 2·5 + 3·3 = 19,
                # so c <= 18 keeps the exponent non-negative (safely >= 4).
                "a":   {"type": "randint", "min": 5, "max": 15},
                "b":   {"type": "randint", "min": 3, "max": 10},
                "c":   {"type": "randint", "min": 3, "max": 15},
                "exp": {"type": "computed", "expr": "2 * {a} + 3 * {b} - {c}"},
            },
            "answer_expr": "5**{exp}",
            "answer_input": "expression",
            "hint": "Rescrieți fiecare bază ca putere a lui $5$:  $25 = 5^2$, $125 = 5^3$. Apoi aplicați regulile: înmulțire → adunare exponenți; împărțire → scădere exponenți.",
            "placeholder": "ex: 5^30",
        },
    },
    {
        "name": "Invers regula 4 cu trei factori: a^n · b^n · c^n",
        "category": "power_rules_simplify",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Invers regula 4 cu trei factori: a^n · b^n · c^n",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere:  ${a}^{{{n}}} \\cdot {b}^{{{n}}} \\cdot {c}^{{{n}}}$",
            "params": {
                # Distinct small bases via disjoint choice sets.
                "a": {"type": "choice", "options": [2, 3, 5]},
                "b": {"type": "choice", "options": [4, 6, 7]},
                "c": {"type": "choice", "options": [8, 9, 11]},
                "n": {"type": "randint", "min": 5, "max": 30},
            },
            "answer_expr": "({a} * {b} * {c})**{n}",
            "answer_input": "expression",
            "hint": "Regula $a^n \\cdot b^n = (a \\cdot b)^n$ se aplică și pentru trei (sau mai multe) factori cu același exponent: $a^n \\cdot b^n \\cdot c^n = (a \\cdot b \\cdot c)^n$.",
            "placeholder": "ex: 60^13",
        },
    },
]
