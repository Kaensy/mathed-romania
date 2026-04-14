"""
Exercise data: order_of_ops_parens
Topic 1.10 — Ordinea efectuării operațiilor

Category: order_of_ops_parens
Label (RO): Ordinea operațiilor — cu paranteze

Tiers:
  Easy   — Single round-paren group, parens change the result meaningfully:
             a · (b + c)        — without parens would be a·b + c
             (a + b) · c        — without parens would be a + b·c
             a · (b - c)
             (a + b)^n           — base of a power is a sum
  Medium — Multiple non-nested paren groups:
             (a + b) · c - d : (e + f)
             a · (b - c) + d · (e - f)
             k · (a + b) - c · (d - e)
  Hard   — Longer expressions with paren groups containing powers:
             (a^n + b) · c - d
             a + b · (c - d^m) : e
             k · (a^n - b) + c^m · (d + e)

Design notes:
  - Each template includes parens that materially change the result. We
    avoid pointless parens like `a + (b · c)` where the parens are redundant
    (multiplication would happen first anyway).
  - All bounds verified for non-negativity at every level — including
    inside paren groups (no `(b - c)` where c could exceed b).
  - Powers inside parens use `m`, `n` not as direct params but where they
    fit the pedagogy.
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 10,
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Single paren group that changes the outcome
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "a · (b + c)",
        "category": "order_of_ops_parens",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a · (b + c)",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot ({b} + {c})$",
            "params": {
                "a":   {"type": "randint", "min": 3, "max": 15},
                "b":   {"type": "randint", "min": 5, "max": 30},
                "c":   {"type": "randint", "min": 5, "max": 30},
                "ans": {"type": "computed", "expr": "{a} * ({b} + {c})"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Calculați mai întâi paranteza: ${b} + {c}$. Apoi înmulțiți rezultatul cu ${a}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "(a + b) · c",
        "category": "order_of_ops_parens",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "(a + b) · c",
            "type": "fill_blank",
            "question": "Calculați:  $({a} + {b}) \\cdot {c}$",
            "params": {
                "a":   {"type": "randint", "min": 5, "max": 30},
                "b":   {"type": "randint", "min": 5, "max": 30},
                "c":   {"type": "randint", "min": 3, "max": 15},
                "ans": {"type": "computed", "expr": "({a} + {b}) * {c}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Paranteza prima: ${a} + {b}$. Apoi înmulțiți cu ${c}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "a · (b - c)",
        "category": "order_of_ops_parens",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a · (b - c)",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot ({b} - {c})$",
            "params": {
                # b > c guaranteed by structured generation.
                "a":   {"type": "randint", "min": 3, "max": 15},
                "c":   {"type": "randint", "min": 5, "max": 30},
                "diff": {"type": "randint", "min": 3, "max": 30},
                "b":   {"type": "computed", "expr": "{c} + {diff}"},
                "ans": {"type": "computed", "expr": "{a} * {diff}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Paranteza prima: ${b} - {c}$. Apoi înmulțiți cu ${a}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "(a + b)^n",
        "category": "order_of_ops_parens",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "(a + b)^n",
            "type": "fill_blank",
            "question": "Calculați:  $({a} + {b})^{{{n}}}$",
            "params": {
                "a":   {"type": "randint", "min": 1, "max": 7},
                "b":   {"type": "randint", "min": 1, "max": 7},
                "n":   {"type": "randint", "min": 2, "max": 4},
                "ans": {"type": "computed", "expr": "({a} + {b}) ** {n}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Paranteza prima: ${a} + {b}$. Apoi ridicați rezultatul la puterea ${n}$.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Multiple non-nested paren groups
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "(a + b) · c - d : (e + f)",
        "category": "order_of_ops_parens",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "(a + b) · c - d : (e + f)",
            "type": "fill_blank",
            "question": "Calculați:  $({a} + {b}) \\cdot {c} - {d} : ({e} + {f})$",
            "params": {
                # Construct exact division: d = (e + f) * q.
                # Lower-bound (a+b)*c so result stays positive.
                "a":   {"type": "randint", "min": 5, "max": 20},
                "b":   {"type": "randint", "min": 5, "max": 20},
                "c":   {"type": "randint", "min": 3, "max": 12},
                "e":   {"type": "randint", "min": 3, "max": 8},
                "f":   {"type": "randint", "min": 3, "max": 8},
                "q":   {"type": "randint", "min": 2, "max": 10},
                "d":   {"type": "computed", "expr": "({e} + {f}) * {q}"},
                # min (a+b)*c = 10*3 = 30; max q = 10 → result >= 20.
                "ans": {"type": "computed", "expr": "({a} + {b}) * {c} - {q}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Calculați separat fiecare paranteză, apoi înmulțirile și împărțirile, apoi adunarea și scăderea.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "a · (b - c) + d · (e - f)",
        "category": "order_of_ops_parens",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a · (b - c) + d · (e - f)",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot ({b} - {c}) + {d} \\cdot ({e} - {f})$",
            "params": {
                # Both subtractions guaranteed positive via structured generation.
                "a":     {"type": "randint", "min": 3, "max": 12},
                "c":     {"type": "randint", "min": 5, "max": 20},
                "diff1": {"type": "randint", "min": 3, "max": 20},
                "b":     {"type": "computed", "expr": "{c} + {diff1}"},
                "d":     {"type": "randint", "min": 3, "max": 12},
                "f":     {"type": "randint", "min": 5, "max": 20},
                "diff2": {"type": "randint", "min": 3, "max": 20},
                "e":     {"type": "computed", "expr": "{f} + {diff2}"},
                "ans":   {"type": "computed", "expr": "{a} * {diff1} + {d} * {diff2}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Calculați mai întâi cele două paranteze (${b} - {c}$ și ${e} - {f}$), apoi cele două înmulțiri, apoi adunați.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "k · (a + b) - c · (d - e)",
        "category": "order_of_ops_parens",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "k · (a + b) - c · (d - e)",
            "type": "fill_blank",
            "question": "Calculați:  ${k} \\cdot ({a} + {b}) - {c} \\cdot ({d} - {e})$",
            "params": {
                # Structured: ensure k*(a+b) >= c*(d-e).
                # Force diff small (1..5) and c small so c*diff <= 50.
                # Force k*(a+b) >= 50 by choosing k>=3, a+b>=20.
                "k":     {"type": "randint", "min": 3, "max": 10},
                "a":     {"type": "randint", "min": 10, "max": 25},
                "b":     {"type": "randint", "min": 10, "max": 25},
                "c":     {"type": "randint", "min": 2, "max": 8},
                "e":     {"type": "randint", "min": 5, "max": 20},
                "diff":  {"type": "randint", "min": 1, "max": 5},
                "d":     {"type": "computed", "expr": "{e} + {diff}"},
                "ans":   {"type": "computed", "expr": "{k} * ({a} + {b}) - {c} * {diff}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Calculați separat ${a} + {b}$ și ${d} - {e}$. Apoi cele două înmulțiri. Apoi scăderea.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "(a + b) · (c - d)",
        "category": "order_of_ops_parens",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "(a + b) · (c - d)",
            "type": "fill_blank",
            "question": "Calculați:  $({a} + {b}) \\cdot ({c} - {d})$",
            "params": {
                "a":     {"type": "randint", "min": 5, "max": 25},
                "b":     {"type": "randint", "min": 5, "max": 25},
                "d":     {"type": "randint", "min": 3, "max": 20},
                "diff":  {"type": "randint", "min": 3, "max": 25},
                "c":     {"type": "computed", "expr": "{d} + {diff}"},
                "ans":   {"type": "computed", "expr": "({a} + {b}) * {diff}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Ambele paranteze se calculează înaintea înmulțirii dintre ele.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Powers inside parens, longer expressions
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "(a^n + b) · c - d",
        "category": "order_of_ops_parens",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "(a^n + b) · c - d",
            "type": "fill_blank",
            "question": "Calculați:  $({a}^{{{n}}} + {b}) \\cdot {c} - {d}$",
            "params": {
                # Force a^n >= 8 (a>=2, n>=3) and c >= 4, b >= 5
                # → min product = (8+5)*4 = 52. Cap d at 50 → result >= 2.
                "a":   {"type": "randint", "min": 2, "max": 5},
                "n":   {"type": "randint", "min": 3, "max": 4},
                "b":   {"type": "randint", "min": 5, "max": 20},
                "c":   {"type": "randint", "min": 4, "max": 8},
                "d":   {"type": "randint", "min": 10, "max": 50},
                "ans": {"type": "computed", "expr": "({a} ** {n} + {b}) * {c} - {d}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "În paranteza rotundă, calculați mai întâi puterea ${a}^{{{n}}}$, apoi adunați ${b}$. Apoi înmulțiți cu ${c}$. Apoi scădeți ${d}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "a + b · (c - d^m) : e",
        "category": "order_of_ops_parens",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a + b · (c - d^m) : e",
            "type": "fill_blank",
            "question": "Calculați:  ${a} + {b} \\cdot ({c} - {d}^{{{m}}}) : {e}$",
            "params": {
                # Construct so c > d^m (paren positive) and (c - d^m) divisible by e.
                # Pick d^m via small d, m=2: d^m in [4, 25].
                # Then pick q so c = d^m + e*q.
                "d":      {"type": "randint", "min": 2, "max": 5},
                "m":      {"type": "fixed", "value": 2},
                "dm":     {"type": "computed", "expr": "{d} ** {m}"},
                "e":      {"type": "randint", "min": 3, "max": 10},
                "q":      {"type": "randint", "min": 2, "max": 10},
                "c":      {"type": "computed", "expr": "{dm} + {e} * {q}"},
                "a":      {"type": "randint", "min": 10, "max": 100},
                "b":      {"type": "randint", "min": 3, "max": 12},
                "ans":    {"type": "computed", "expr": "{a} + {b} * {q}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "În paranteză: calculați ${d}^{{{m}}}$, apoi scădeți din ${c}$. Înmulțiți cu ${b}$, împărțiți la ${e}$. La final adunați ${a}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "k · (a^n - b) + c^m · (d + e)",
        "category": "order_of_ops_parens",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "k · (a^n - b) + c^m · (d + e)",
            "type": "fill_blank",
            "question": "Calculați:  ${k} \\cdot ({a}^{{{n}}} - {b}) + {c}^{{{m}}} \\cdot ({d} + {e})$",
            "params": {
                # Force a^n > b: pick b = a^n - delta with delta small positive.
                "a":     {"type": "randint", "min": 3, "max": 5},
                "n":     {"type": "fixed", "value": 3},
                "an":    {"type": "computed", "expr": "{a} ** {n}"},
                "delta": {"type": "randint", "min": 5, "max": 20},
                "b":     {"type": "computed", "expr": "{an} - {delta}"},
                "k":     {"type": "randint", "min": 2, "max": 6},
                "c":     {"type": "randint", "min": 2, "max": 4},
                "m":     {"type": "fixed", "value": 2},
                "d":     {"type": "randint", "min": 5, "max": 20},
                "e":     {"type": "randint", "min": 5, "max": 20},
                "ans":   {"type": "computed", "expr": "{k} * {delta} + {c} ** {m} * ({d} + {e})"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "În fiecare paranteză: puterea prima, apoi adunarea/scăderea. Apoi cele două înmulțiri. La final adunați rezultatele.",
            "placeholder": "= ?",
        },
    },
]
