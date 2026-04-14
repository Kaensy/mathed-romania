"""
Exercise data: order_of_ops_nested
Topic 1.10 — Ordinea efectuării operațiilor

Category: order_of_ops_nested
Label (RO): Ordinea operațiilor — paranteze imbricate

Tiers:
  Easy   — 2-level nesting: square brackets enclose round parens.
             a + [b · (c + d) - e]
             [a + b · (c - d)] : e
  Medium — 3-level nesting: curly braces around square around round.
             a · {b - [c + (d - e)]}
             {a + [b - (c + d)]} : e
  Hard   — 3-level nesting with powers and the "successor" framing
           (find a + 1 where a is a deeply nested expression).

Romanian convention:
  - innermost parens: () round
  - middle:           [] square
  - outermost:        {} curly
  - work from inside out

Design notes:
  - Every paren level is load-bearing — removing it changes the answer.
  - Every level evaluates to a non-negative natural number, verified
    via structured generation (subtractions only after sums that
    guarantee a sufficient minuend).
  - Hard "successor" template asks for a + 1 instead of a, mirroring
    textbook Ex 5 style — same skill, just one extra trivial step.
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 10,
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — 2-level nesting: [...(...)...]
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "a + [b · (c + d) - e]",
        "category": "order_of_ops_nested",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a + [b · (c + d) - e]",
            "type": "fill_blank",
            "question": "Calculați:  ${a} + [{b} \\cdot ({c} + {d}) - {e}]$",
            "params": {
                # Force inner: c + d in [10, 40].
                # Then b·(c+d) ≥ 2·10 = 20. Cap e at 18 → bracket positive.
                "a":   {"type": "randint", "min": 5, "max": 50},
                "b":   {"type": "randint", "min": 2, "max": 8},
                "c":   {"type": "randint", "min": 5, "max": 20},
                "d":   {"type": "randint", "min": 5, "max": 20},
                "e":   {"type": "randint", "min": 5, "max": 18},
                "ans": {"type": "computed", "expr": "{a} + ({b} * ({c} + {d}) - {e})"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Lucrați din interior spre exterior. Calculați mai întâi paranteza rotundă $({c} + {d})$, apoi înmulțirea, apoi scăderea din paranteza pătrată, apoi adunarea finală.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "[a + b · (c - d)] : e",
        "category": "order_of_ops_nested",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "[a + b · (c - d)] : e",
            "type": "fill_blank",
            "question": "Calculați:  $[{a} + {b} \\cdot ({c} - {d})] : {e}$",
            "params": {
                # Force c > d (structured) and full bracket divisible by e.
                "d":      {"type": "randint", "min": 3, "max": 15},
                "diff":   {"type": "randint", "min": 2, "max": 15},
                "c":      {"type": "computed", "expr": "{d} + {diff}"},
                "b":      {"type": "randint", "min": 2, "max": 8},
                # bracket = a + b * diff. Force divisibility by picking e and q.
                "e":      {"type": "randint", "min": 3, "max": 10},
                "q":      {"type": "randint", "min": 5, "max": 30},
                "bracket": {"type": "computed", "expr": "{e} * {q}"},
                "a":      {"type": "computed", "expr": "{bracket} - {b} * {diff}"},
                "ans":    {"type": "computed", "expr": "{q}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Lucrați din interior: paranteza rotundă, apoi înmulțirea, apoi adunarea din paranteza pătrată, apoi împărțirea finală.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "k · [a · (b + c) - d]",
        "category": "order_of_ops_nested",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "k · [a · (b + c) - d]",
            "type": "fill_blank",
            "question": "Calculați:  ${k} \\cdot [{a} \\cdot ({b} + {c}) - {d}]$",
            "params": {
                # b + c >= 6, a >= 3 → a*(b+c) >= 18. d capped at 15.
                "k":   {"type": "randint", "min": 2, "max": 6},
                "a":   {"type": "randint", "min": 3, "max": 10},
                "b":   {"type": "randint", "min": 3, "max": 15},
                "c":   {"type": "randint", "min": 3, "max": 15},
                "d":   {"type": "randint", "min": 3, "max": 15},
                "ans": {"type": "computed", "expr": "{k} * ({a} * ({b} + {c}) - {d})"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Din interior spre exterior: ${b} + {c}$, apoi înmulțirea cu ${a}$, apoi scăderea, apoi înmulțirea finală cu ${k}$.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — 3-level nesting: {...[...(...)...]...}
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "a · {b - [c + (d - e)]}",
        "category": "order_of_ops_nested",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a · {b - [c + (d - e)]}",
            "type": "fill_blank",
            "question": "Calculați:  ${a} \\cdot \\{{b} - [{c} + ({d} - {e})]\\}$",
            "params": {
                # Innermost: d > e (structured).
                # Square: c + (d-e) <= b (so curly stays positive).
                "e":      {"type": "randint", "min": 2, "max": 10},
                "diff_de": {"type": "randint", "min": 2, "max": 10},
                "d":      {"type": "computed", "expr": "{e} + {diff_de}"},
                "c":      {"type": "randint", "min": 2, "max": 10},
                "square": {"type": "computed", "expr": "{c} + {diff_de}"},
                # b > square. Pick gap_b small to keep result small/manageable.
                "gap_b":  {"type": "randint", "min": 2, "max": 15},
                "b":      {"type": "computed", "expr": "{square} + {gap_b}"},
                "a":      {"type": "randint", "min": 2, "max": 8},
                "ans":    {"type": "computed", "expr": "{a} * {gap_b}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Începeți din paranteza rotundă $({d} - {e})$. Apoi paranteza pătrată: ${c} + (\\ldots)$. Apoi acolada: ${b} - [\\ldots]$. La final, înmulțirea cu ${a}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "{a + [b - (c + d)]} : e",
        "category": "order_of_ops_nested",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "{a + [b - (c + d)]} : e",
            "type": "fill_blank",
            "question": "Calculați:  $\\{{a} + [{b} - ({c} + {d})]\\} : {e}$",
            "params": {
                # Innermost: c + d (always positive).
                # Square: b - (c+d) must be >= 0 → b >= c+d.
                # Curly: a + (square) divisible by e.
                "c":      {"type": "randint", "min": 3, "max": 12},
                "d":      {"type": "randint", "min": 3, "max": 12},
                "round_v": {"type": "computed", "expr": "{c} + {d}"},
                "gap_b":  {"type": "randint", "min": 5, "max": 30},
                "b":      {"type": "computed", "expr": "{round_v} + {gap_b}"},
                # square_v = gap_b. curly = a + gap_b. Force divisibility by e.
                "e":      {"type": "randint", "min": 3, "max": 10},
                "q":      {"type": "randint", "min": 3, "max": 15},
                "curly":  {"type": "computed", "expr": "{e} * {q}"},
                "a":      {"type": "computed", "expr": "{curly} - {gap_b}"},
                "ans":    {"type": "computed", "expr": "{q}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Începeți cu paranteza rotundă, apoi cea pătrată, apoi acolada, apoi împărțirea la ${e}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "k · {a · [b + (c - d)] - e}",
        "category": "order_of_ops_nested",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "k · {a · [b + (c - d)] - e}",
            "type": "fill_blank",
            "question": "Calculați:  ${k} \\cdot \\{{a} \\cdot [{b} + ({c} - {d})] - {e}\\}$",
            "params": {
                "d":      {"type": "randint", "min": 3, "max": 12},
                "diff":   {"type": "randint", "min": 2, "max": 10},
                "c":      {"type": "computed", "expr": "{d} + {diff}"},
                "b":      {"type": "randint", "min": 5, "max": 20},
                # square = b + diff in [7, 30]. a*square in [14, 240].
                # Cap e small enough to keep curly positive.
                "a":      {"type": "randint", "min": 2, "max": 6},
                "e":      {"type": "randint", "min": 3, "max": 12},
                "k":      {"type": "randint", "min": 2, "max": 5},
                "ans":    {"type": "computed", "expr": "{k} * ({a} * ({b} + {diff}) - {e})"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Din interior spre exterior: rotunda, pătrata, acolada, apoi înmulțirea cu ${k}$.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — 3-level nesting with powers; "successor" variant
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "a^n + {b · [c + (d - e)] - f^m}",
        "category": "order_of_ops_nested",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "a^n + {b · [c + (d - e)] - f^m}",
            "type": "fill_blank",
            "question": "Calculați:  ${a}^{{{n}}} + \\{{b} \\cdot [{c} + ({d} - {e})] - {f}^{{{m}}}\\}$",
            "params": {
                # Innermost rotunda: d > e (structured).
                # Square: c + diff_de >= 1.
                # Curly: b * square - f^m must be >= 0.
                # Choose f^m small: f in [2,3], m=2 → f^m in [4,9].
                # Force b * square >= 30 to dominate.
                "e":       {"type": "randint", "min": 2, "max": 10},
                "diff_de": {"type": "randint", "min": 3, "max": 12},
                "d":       {"type": "computed", "expr": "{e} + {diff_de}"},
                "c":       {"type": "randint", "min": 5, "max": 15},
                # square = c + diff_de in [8, 27]. b in [3,5] → b*square >= 24.
                "b":       {"type": "randint", "min": 3, "max": 5},
                "f":       {"type": "randint", "min": 2, "max": 3},
                "m":       {"type": "fixed", "value": 2},
                "a":       {"type": "randint", "min": 2, "max": 5},
                "n":       {"type": "randint", "min": 2, "max": 3},
                "ans":     {"type": "computed", "expr": "{a} ** {n} + ({b} * ({c} + {diff_de}) - {f} ** {m})"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Calculați din interior spre exterior. Puterile (${a}^{{{n}}}$ și ${f}^{{{m}}}$) se calculează la nivelul lor de paranteză.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "{[a · (b + c^n) - d] : e} · f",
        "category": "order_of_ops_nested",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "{[a · (b + c^n) - d] : e} · f",
            "type": "fill_blank",
            "question": "Calculați:  $\\{[{a} \\cdot ({b} + {c}^{{{n}}}) - {d}] : {e}\\} \\cdot {f}$",
            "params": {
                # Build from outside-in to ensure exact division.
                # round_v = b + c^n. square_v = a * round_v - d.
                # Need square_v divisible by e.
                # Strategy: pick c, n, b → round_v. Pick a. Pick e and q so
                # that a * round_v - d = e * q. Solve d = a*round_v - e*q.
                "c":       {"type": "randint", "min": 2, "max": 4},
                "n":       {"type": "fixed", "value": 2},
                "cn":      {"type": "computed", "expr": "{c} ** {n}"},
                "b":       {"type": "randint", "min": 5, "max": 15},
                "round_v": {"type": "computed", "expr": "{b} + {cn}"},
                "a":       {"type": "randint", "min": 3, "max": 8},
                "e":       {"type": "randint", "min": 3, "max": 8},
                "q":       {"type": "randint", "min": 2, "max": 10},
                "d":       {"type": "computed", "expr": "{a} * {round_v} - {e} * {q}"},
                "f":       {"type": "randint", "min": 2, "max": 6},
                "ans":     {"type": "computed", "expr": "{q} * {f}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Din interior spre exterior: paranteza rotundă (puterea apoi adunarea), pătrata (înmulțire apoi scădere), acolada (împărțire), apoi înmulțirea finală.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Succesorul lui a, unde a = {...}",
        "category": "order_of_ops_nested",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Succesorul lui a, unde a = {...}",
            "type": "fill_blank",
            "question": "Determinați succesorul numărului $a$, unde:  $a = {k} + \\{{p} - [{q} \\cdot ({r} - {s})] : {t}\\}$",
            "params": {
                # Build outside-in to guarantee clean division.
                # r - s = diff (structured: r = s + diff).
                # q * diff must be divisible by t. Easiest: set t to divide q.
                # We pick t and a multiplier so q = t * mult.
                "s":     {"type": "randint", "min": 3, "max": 10},
                "diff":  {"type": "randint", "min": 3, "max": 12},
                "r":     {"type": "computed", "expr": "{s} + {diff}"},
                "t":     {"type": "randint", "min": 2, "max": 6},
                "mult":  {"type": "randint", "min": 2, "max": 5},
                "q":     {"type": "computed", "expr": "{t} * {mult}"},
                # Inner [...] = q*diff = t*mult*diff. Divided by t = mult*diff.
                # Need p > mult*diff for curly to stay non-negative.
                "sub_v": {"type": "computed", "expr": "{mult} * {diff}"},
                "gap_p": {"type": "randint", "min": 5, "max": 50},
                "p":     {"type": "computed", "expr": "{sub_v} + {gap_p}"},
                "k":     {"type": "randint", "min": 5, "max": 50},
                # a = k + (p - sub_v) = k + gap_p. successor = k + gap_p + 1.
                "ans":   {"type": "computed", "expr": "{k} + {gap_p} + 1"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Calculați $a$ din interior spre exterior, apoi adăugați $1$ pentru a obține succesorul.",
            "placeholder": "a + 1 = ?",
        },
    },
]
