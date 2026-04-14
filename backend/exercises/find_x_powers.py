"""
Exercise data: find_x_powers
Topic 1.8 — Puterea cu exponent natural (sub-lesson A: definiție și reguli)

Category: find_x_powers
Label (RO): Aflarea necunoscutei (puteri)

Tiers:
  Easy   — Direct exponential equations:
             a^x = value            (solve for x as exponent)
             x^n = value            (solve for x as base)
             1^x = 1 convention     (any x — use a specific target)
  Medium — Single-rule applications where x is an exponent:
             a^x · a^k = a^N        → x = N - k    (rule 1)
             (a^x)^k = a^N          → x = N / k    (rule 3)
             a^N : a^x = a^M        → x = N - M    (rule 2)
  Hard   — Two-step chains requiring rule composition:
             (a^x)^k · a^p = a^N    → x·k + p = N
             (a^k)^x : a^p = a^N    → k·x - p = N
             a^(x+1) + a^x = k·a^x  → solve for the scalar relationship

Design notes:
  - Question strings use literal `x` (not `{x}`) — the `{x}` brace syntax
    triggers set-literal eval bugs in the engine (documented gotcha).
  - Param key `x_ans` holds the intended value of x (the answer). We
    never put this name inside a question string's braces.
  - Answer input is `number` throughout — x is always a small natural number.

Usage:
    python manage.py load_exercises exercises.find_x_powers
    python manage.py load_exercises exercises.find_x_powers --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 8,
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Direct exponential equations
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Aflați exponentul: a^x = valoare",
        "category": "find_x_powers",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Aflați exponentul: a^x = valoare",
            "type": "fill_blank",
            "question": "Aflați numărul natural $x$ astfel încât:  ${a}^x = {val}$",
            "params": {
                "a":     {"type": "randint", "min": 2, "max": 7},
                "x_ans": {"type": "randint", "min": 2, "max": 5},
                "val":   {"type": "computed", "expr": "{a} ** {x_ans}"},
            },
            "answer_expr": "{x_ans}",
            "answer_input": "number",
            "hint": "Căutați exponentul care aplicat lui ${a}$ dă ${val}$. Încercați pe rând: ${a}^2$, ${a}^3$, ...",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Aflați baza: x^n = valoare",
        "category": "find_x_powers",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Aflați baza: x^n = valoare",
            "type": "fill_blank",
            "question": "Aflați numărul natural $x$ astfel încât:  $x^{{{n}}} = {val}$",
            "params": {
                "x_ans": {"type": "randint", "min": 2, "max": 9},
                "n":     {"type": "randint", "min": 2, "max": 4},
                "val":   {"type": "computed", "expr": "{x_ans} ** {n}"},
            },
            "answer_expr": "{x_ans}",
            "answer_input": "number",
            "hint": "Căutați baza care ridicată la puterea ${n}$ dă ${val}$. Încercați $2^{{{n}}}$, $3^{{{n}}}$, ...",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Convenție: x^0 = 1",
        "category": "find_x_powers",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Convenție: x^0 = 1",
            "type": "fill_blank",
            "question": "Aflați numărul natural $x$ astfel încât:  $x^{{{n}}} = 1$, cu $x > 0$.",
            "params": {
                "n": {"type": "choice", "options": [7, 10, 100, 2011]},
            },
            "answer_expr": "1",
            "answer_input": "number",
            "hint": "Ce număr natural nenul, ridicat la orice putere, rămâne $1$?",
            "placeholder": "x = ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Single power rule applications
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Regula 1 invers: a^x · a^k = a^N",
        "category": "find_x_powers",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Regula 1 invers: a^x · a^k = a^N",
            "type": "fill_blank",
            "question": "Aflați numărul natural $x$ astfel încât:  ${a}^x \\cdot {a}^{{{k}}} = {a}^{{{N}}}$",
            "params": {
                "a":     {"type": "randint", "min": 2, "max": 12},
                "k":     {"type": "randint", "min": 3, "max": 20},
                "x_ans": {"type": "randint", "min": 2, "max": 20},
                "N":     {"type": "computed", "expr": "{x_ans} + {k}"},
            },
            "answer_expr": "{x_ans}",
            "answer_input": "number",
            "hint": "Regula 1: ${a}^x \\cdot {a}^{{{k}}} = {a}^{{x + {k}}}$. Deci $x + {k} = {N}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Regula 2 invers: a^N : a^x = a^M",
        "category": "find_x_powers",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Regula 2 invers: a^N : a^x = a^M",
            "type": "fill_blank",
            "question": "Aflați numărul natural $x$ astfel încât:  ${a}^{{{N}}} : {a}^x = {a}^{{{M}}}$",
            "params": {
                "a":     {"type": "randint", "min": 2, "max": 12},
                "M":     {"type": "randint", "min": 3, "max": 20},
                "x_ans": {"type": "randint", "min": 2, "max": 20},
                "N":     {"type": "computed", "expr": "{M} + {x_ans}"},
            },
            "answer_expr": "{x_ans}",
            "answer_input": "number",
            "hint": "Regula 2: ${a}^{{{N}}} : {a}^x = {a}^{{{N} - x}}$. Deci ${N} - x = {M}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Regula 3 invers: (a^x)^k = a^N",
        "category": "find_x_powers",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Regula 3 invers: (a^x)^k = a^N",
            "type": "fill_blank",
            "question": "Aflați numărul natural $x$ astfel încât:  $({a}^x)^{{{k}}} = {a}^{{{N}}}$",
            "params": {
                "a":     {"type": "randint", "min": 2, "max": 12},
                "k":     {"type": "randint", "min": 3, "max": 12},
                "x_ans": {"type": "randint", "min": 2, "max": 15},
                "N":     {"type": "computed", "expr": "{x_ans} * {k}"},
            },
            "answer_expr": "{x_ans}",
            "answer_input": "number",
            "hint": "Regula 3: $({a}^x)^{{{k}}} = {a}^{{x \\cdot {k}}}$. Deci $x \\cdot {k} = {N}$, de unde $x = {N} : {k}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Regula 3 invers cu exponent mare: (a^k)^x = a^N",
        "category": "find_x_powers",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Regula 3 invers cu exponent mare: (a^k)^x = a^N",
            "type": "fill_blank",
            "question": "Aflați numărul natural $x$ astfel încât:  $({a}^{{{k}}})^x = {a}^{{{N}}}$",
            "params": {
                "a":     {"type": "randint", "min": 2, "max": 10},
                "k":     {"type": "randint", "min": 3, "max": 10},
                "x_ans": {"type": "randint", "min": 2, "max": 12},
                "N":     {"type": "computed", "expr": "{k} * {x_ans}"},
            },
            "answer_expr": "{x_ans}",
            "answer_input": "number",
            "hint": "Regula 3: $({a}^{{{k}}})^x = {a}^{{{k} \\cdot x}}$. Deci ${k} \\cdot x = {N}$, de unde $x = {N} : {k}$.",
            "placeholder": "x = ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Two-step chains
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Lanț: (a^x)^k · a^p = a^N",
        "category": "find_x_powers",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Lanț: (a^x)^k · a^p = a^N",
            "type": "fill_blank",
            "question": "Aflați numărul natural $x$ astfel încât:  $({a}^x)^{{{k}}} \\cdot {a}^{{{p}}} = {a}^{{{N}}}$",
            "params": {
                "a":     {"type": "randint", "min": 2, "max": 10},
                "k":     {"type": "randint", "min": 2, "max": 8},
                "p":     {"type": "randint", "min": 2, "max": 15},
                "x_ans": {"type": "randint", "min": 2, "max": 10},
                "N":     {"type": "computed", "expr": "{x_ans} * {k} + {p}"},
            },
            "answer_expr": "{x_ans}",
            "answer_input": "number",
            "hint": "Aplicați întâi regula 3: $({a}^x)^{{{k}}} = {a}^{{x \\cdot {k}}}$. Apoi regula 1 cu ${a}^{{{p}}}$ dă ${a}^{{x \\cdot {k} + {p}}} = {a}^{{{N}}}$. Rezolvați $x \\cdot {k} + {p} = {N}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Lanț cu împărțire: (a^k)^x : a^p = a^N",
        "category": "find_x_powers",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Lanț cu împărțire: (a^k)^x : a^p = a^N",
            "type": "fill_blank",
            "question": "Aflați numărul natural $x$ astfel încât:  $({a}^{{{k}}})^x : {a}^{{{p}}} = {a}^{{{N}}}$",
            "params": {
                "a":     {"type": "randint", "min": 2, "max": 10},
                "k":     {"type": "randint", "min": 2, "max": 6},
                "p":     {"type": "randint", "min": 2, "max": 10},
                "x_ans": {"type": "randint", "min": 3, "max": 10},
                "N":     {"type": "computed", "expr": "{k} * {x_ans} - {p}"},
            },
            "answer_expr": "{x_ans}",
            "answer_input": "number",
            "hint": "Aplicați regula 3: $({a}^{{{k}}})^x = {a}^{{{k} \\cdot x}}$. Apoi regula 2: ${a}^{{{k} \\cdot x}} : {a}^{{{p}}} = {a}^{{{k} \\cdot x - {p}}}$. Rezolvați ${k} \\cdot x - {p} = {N}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Rebazare pentru a afla x: 2^x = 4^k",
        "category": "find_x_powers",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Rebazare pentru a afla x: 2^x = 4^k",
            "type": "fill_blank",
            "question": "Aflați numărul natural $x$ astfel încât:  $2^x = {base}^{{{k}}}$",
            "params": {
                "base":  {"type": "choice", "options": [4, 8, 16]},
                "k":     {"type": "randint", "min": 5, "max": 15},
                "p":     {"type": "computed", "expr": "2 if {base} == 4 else (3 if {base} == 8 else 4)"},
                "x_ans": {"type": "computed", "expr": "{p} * {k}"},
            },
            "answer_expr": "{x_ans}",
            "answer_input": "number",
            "hint": "Rescrieți baza din dreapta ca putere a lui $2$: $4 = 2^2$, $8 = 2^3$, $16 = 2^4$. Apoi aplicați regula 3 și comparați exponenții.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Factor comun cu x: a^(x+1) + a^x = k·a^n",
        "category": "find_x_powers",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Factor comun cu x: a^(x+1) + a^x = k·a^n",
            "type": "fill_blank",
            "question": "Aflați numărul natural $x$ astfel încât:  ${a}^{{x+1}} + {a}^x = {k} \\cdot {a}^{{{n}}}$",
            "params": {
                # Factoring gives a^x · (a+1). For this to equal k · a^n with k = a+1:
                # we need x = n.
                "a":     {"type": "randint", "min": 2, "max": 6},
                "x_ans": {"type": "randint", "min": 5, "max": 20},
                "k":     {"type": "computed", "expr": "{a} + 1"},
                "n":     {"type": "computed", "expr": "{x_ans}"},
            },
            "answer_expr": "{x_ans}",
            "answer_input": "number",
            "hint": "Scoateți ${a}^x$ factor comun: ${a}^{{x+1}} + {a}^x = {a}^x \\cdot ({a} + 1) = {k} \\cdot {a}^x$. Comparați cu ${k} \\cdot {a}^{{{n}}}$ pentru a afla $x$.",
            "placeholder": "x = ?",
        },
    },
]
