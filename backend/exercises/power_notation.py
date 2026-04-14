"""
Exercise data: power_notation
Topic 1.8 — Puterea cu exponent natural (sub-lesson A: definiție și reguli)

Category: power_notation
Label (RO): Notația puterii

Tiers:
  Easy   — Identify base/exponent of a power, rewrite short product as power
  Medium — Long products with specified factor count; chain a·a²·a³·...·a^k
  Hard   — Geometric chain 2·4·8·...·2^k (bases must be recognized as
           powers of a common base first, then exponents summed via Gauss)

Notes:
  - Question strings use inline $...$ KaTeX only (no $$...$$).
  - ${a}^{{{n}}}$ pattern: outer {{ }} survive as literal braces in LaTeX
    output so multi-digit exponents render correctly, e.g. 2^{2011}.
  - `answer_input: "expression"` — SymPy accepts 2^40, 2**40, or the
    numeric value 1099511627776 as equivalent.

Usage:
    python manage.py load_exercises exercises.power_notation
    python manage.py load_exercises exercises.power_notation --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 8,  # "Puterea cu exponent natural"
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Foundational notation
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Identifică baza puterii",
        "category": "power_notation",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Identifică baza puterii",
            "type": "fill_blank",
            "question": "Care este baza puterii  ${a}^{{{n}}}$ ?",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 99},
                "n": {"type": "randint", "min": 2, "max": 50},
            },
            "answer_expr": "{a}",
            "answer_input": "number",
            "hint": "În scrierea $a^n$, numărul $a$ se numește *bază*, iar $n$ se numește *exponent*.",
            "placeholder": "Baza = ?",
        },
    },
    {
        "name": "Identifică exponentul puterii",
        "category": "power_notation",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Identifică exponentul puterii",
            "type": "fill_blank",
            "question": "Care este exponentul puterii  ${a}^{{{n}}}$ ?",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 99},
                "n": {"type": "randint", "min": 2, "max": 100},
            },
            "answer_expr": "{n}",
            "answer_input": "number",
            "hint": "În scrierea $a^n$, numărul $n$ se numește *exponent*, iar $a$ se numește *bază*.",
            "placeholder": "Exponentul = ?",
        },
    },
    {
        "name": "Produs scurt ca putere",
        "category": "power_notation",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Produs scurt ca putere",
            "type": "fill_blank",
            "question": "Scrieți sub formă de putere produsul:  ${a} \\cdot {a} \\cdot \\ldots \\cdot {a}$   (${n}$ factori).",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 9},
                "n": {"type": "randint", "min": 3, "max": 6},
            },
            "answer_expr": "{a}**{n}",
            "answer_input": "expression",
            "hint": "Un produs de $n$ factori egali cu $a$ se scrie $a^n$.",
            "placeholder": "ex: 2^5",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Long products, visible-exponent chain
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Produs cu număr mare de factori",
        "category": "power_notation",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Produs cu număr mare de factori",
            "type": "fill_blank",
            "question": "Scrieți sub formă de putere:  ${a} \\cdot {a} \\cdot \\ldots \\cdot {a}$   (${n}$ factori).",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 20},
                "n": {"type": "choice", "options": [37, 58, 100, 2011, 2024]},
            },
            "answer_expr": "{a}**{n}",
            "answer_input": "expression",
            "hint": "Un produs de ${n}$ factori egali cu ${a}$ se scrie ${a}^{{{n}}}$.",
            "placeholder": "ex: 2^100",
        },
    },
    {
        "name": "Lanț cu exponenți vizibili: a · a² · a³ · ... · a^k",
        "category": "power_notation",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Lanț cu exponenți vizibili: a · a² · a³ · ... · a^k",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere a lui ${a}$:   ${a} \\cdot {a}^2 \\cdot {a}^3 \\cdot \\ldots \\cdot {a}^{{{k}}}$",
            "params": {
                "a":   {"type": "randint", "min": 2, "max": 7},
                "k":   {"type": "randint", "min": 5, "max": 10},
                "exp": {"type": "computed", "expr": "{k} * ({k} + 1) // 2"},
            },
            "answer_expr": "{a}**{exp}",
            "answer_input": "expression",
            "hint": "Folosiți ${a}^m \\cdot {a}^p = {a}^{{m+p}}$. Trebuie să adunați toți exponenții: $1 + 2 + 3 + \\ldots + {k}$ (sumă Gauss).",
            "placeholder": "ex: 2^15",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Geometric chain: recognize each factor as a power of the base
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Lanț geometric: 2 · 4 · 8 · ... · 2^k",
        "category": "power_notation",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Lanț geometric: 2 · 4 · 8 · ... · 2^k",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere a lui $2$:   $2 \\cdot 4 \\cdot 8 \\cdot 16 \\cdot \\ldots \\cdot {last}$",
            "params": {
                "k":    {"type": "randint", "min": 5, "max": 10},
                "last": {"type": "computed", "expr": "2 ** {k}"},
                "exp":  {"type": "computed", "expr": "{k} * ({k} + 1) // 2"},
            },
            "answer_expr": "2**{exp}",
            "answer_input": "expression",
            "hint": "Rescrieți fiecare factor ca putere a lui $2$:  $2 = 2^1$, $4 = 2^2$, $8 = 2^3$, $\\ldots$, ${last} = 2^{{{k}}}$. Apoi adunați toți exponenții.",
            "placeholder": "ex: 2^21",
        },
    },
    {
        "name": "Lanț geometric: 3 · 9 · 27 · ... · 3^k",
        "category": "power_notation",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Lanț geometric: 3 · 9 · 27 · ... · 3^k",
            "type": "fill_blank",
            "question": "Scrieți ca o singură putere a lui $3$:   $3 \\cdot 9 \\cdot 27 \\cdot 81 \\cdot \\ldots \\cdot {last}$",
            "params": {
                "k":    {"type": "randint", "min": 5, "max": 8},
                "last": {"type": "computed", "expr": "3 ** {k}"},
                "exp":  {"type": "computed", "expr": "{k} * ({k} + 1) // 2"},
            },
            "answer_expr": "3**{exp}",
            "answer_input": "expression",
            "hint": "Rescrieți fiecare factor: $3 = 3^1$, $9 = 3^2$, $27 = 3^3$, $\\ldots$, ${last} = 3^{{{k}}}$. Adunați exponenții.",
            "placeholder": "ex: 3^15",
        },
    },
]
