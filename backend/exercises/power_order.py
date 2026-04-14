"""
Exercise data: power_order
Topic 1.8 — Puterea cu exponent natural (sub-lesson C: comparare, pătrate)

Category: power_order
Label (RO): Ordonarea puterilor

Tiers:
  Easy   — 3 powers, same base or same exponent (direct comparison rules)
  Medium — 3 powers, mixed bases requiring one rebasing step
  Hard   — 4 powers, mixed bases + mixed exponents, full comparison toolkit

Design notes:
  - Uses `drag_order` exercise type. Engine sort_key uses eval() so powers
    compare correctly by actual numeric value.
  - Items strings use `**` syntax — the engine's _to_katex helper converts
    to KaTeX `^{}` for display automatically (via recent engine patch).
  - All parameter ranges are constructed so effective (same-base) exponents
    are STRICTLY DISJOINT — no two items can ever be numerically equal.
    This ensures the correct ordering is always unambiguous.
  - Direction alternates between templates for variety.

Usage:
    python manage.py load_exercises exercises.power_order
    python manage.py load_exercises exercises.power_order --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 8,
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — 3 powers, direct comparison (same base OR same exponent)
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Ordonare crescătoare: 3 puteri cu aceeași bază",
        "category": "power_order",
        "difficulty": "easy",
        "exercise_type": "drag_order",
        "template": {
            "title": "Ordonare crescătoare: 3 puteri cu aceeași bază",
            "type": "drag_order",
            "display_mode": "drag_number",
            "question": "Ordonați crescător numerele:",
            "params": {
                # Disjoint exponent ranges guarantee distinct values.
                "a":  {"type": "randint", "min": 2, "max": 12},
                "e1": {"type": "randint", "min": 10, "max": 25},
                "e2": {"type": "randint", "min": 35, "max": 55},
                "e3": {"type": "randint", "min": 70, "max": 100},
            },
            "items": ["{a}**{e2}", "{a}**{e1}", "{a}**{e3}"],
            "order_direction": "ascending",
        },
    },
    {
        "name": "Ordonare descrescătoare: 3 puteri cu aceeași bază",
        "category": "power_order",
        "difficulty": "easy",
        "exercise_type": "drag_order",
        "template": {
            "title": "Ordonare descrescătoare: 3 puteri cu aceeași bază",
            "type": "drag_order",
            "display_mode": "drag_number",
            "question": "Ordonați descrescător numerele:",
            "params": {
                "a":  {"type": "randint", "min": 2, "max": 12},
                "e1": {"type": "randint", "min": 10, "max": 25},
                "e2": {"type": "randint", "min": 35, "max": 55},
                "e3": {"type": "randint", "min": 70, "max": 100},
            },
            "items": ["{a}**{e2}", "{a}**{e3}", "{a}**{e1}"],
            "order_direction": "descending",
        },
    },
    {
        "name": "Ordonare crescătoare: 3 puteri cu același exponent",
        "category": "power_order",
        "difficulty": "easy",
        "exercise_type": "drag_order",
        "template": {
            "title": "Ordonare crescătoare: 3 puteri cu același exponent",
            "type": "drag_order",
            "display_mode": "drag_number",
            "question": "Ordonați crescător numerele:",
            "params": {
                # Disjoint base ranges.
                "a": {"type": "randint", "min": 2, "max": 9},
                "b": {"type": "randint", "min": 15, "max": 30},
                "c": {"type": "randint", "min": 40, "max": 99},
                "n": {"type": "randint", "min": 15, "max": 80},
            },
            "items": ["{b}**{n}", "{a}**{n}", "{c}**{n}"],
            "order_direction": "ascending",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — 3 powers, one rebasing step
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Ordonare: puteri ale lui 2, 4, 8",
        "category": "power_order",
        "difficulty": "medium",
        "exercise_type": "drag_order",
        "template": {
            "title": "Ordonare: puteri ale lui 2, 4, 8",
            "type": "drag_order",
            "display_mode": "drag_number",
            "question": "Ordonați crescător numerele:",
            "params": {
                # Effective 2-exponents (strictly disjoint):
                #   2^e1   →    e1  ∈ [30, 45]
                #   4^e2   →  2·e2  ∈ [50, 64]   (e2 ∈ [25, 32])
                #   8^e3   →  3·e3  ∈ [69, 84]   (e3 ∈ [23, 28])
                "e1": {"type": "randint", "min": 30, "max": 45},
                "e2": {"type": "randint", "min": 25, "max": 32},
                "e3": {"type": "randint", "min": 23, "max": 28},
            },
            "items": ["2**{e1}", "4**{e2}", "8**{e3}"],
            "order_direction": "ascending",
        },
    },
    {
        "name": "Ordonare: puteri ale lui 3 și 9",
        "category": "power_order",
        "difficulty": "medium",
        "exercise_type": "drag_order",
        "template": {
            "title": "Ordonare: puteri ale lui 3 și 9",
            "type": "drag_order",
            "display_mode": "drag_number",
            "question": "Ordonați crescător numerele:",
            "params": {
                # Effective 3-exponents (strictly disjoint):
                #   3^e1   →    e1  ∈ [15, 22]
                #   9^e2   →  2·e2  ∈ [26, 34]   (e2 ∈ [13, 17])
                #   3^e3   →    e3  ∈ [40, 60]
                "e1": {"type": "randint", "min": 15, "max": 22},
                "e2": {"type": "randint", "min": 13, "max": 17},
                "e3": {"type": "randint", "min": 40, "max": 60},
            },
            "items": ["3**{e1}", "9**{e2}", "3**{e3}"],
            "order_direction": "ascending",
        },
    },
    {
        "name": "Ordonare: puteri ale lui 5 și 25",
        "category": "power_order",
        "difficulty": "medium",
        "exercise_type": "drag_order",
        "template": {
            "title": "Ordonare: puteri ale lui 5 și 25",
            "type": "drag_order",
            "display_mode": "drag_number",
            "question": "Ordonați descrescător numerele:",
            "params": {
                # Same structure as 3/9 case.
                "e1": {"type": "randint", "min": 15, "max": 22},
                "e2": {"type": "randint", "min": 13, "max": 17},
                "e3": {"type": "randint", "min": 40, "max": 60},
            },
            "items": ["5**{e1}", "25**{e2}", "5**{e3}"],
            "order_direction": "descending",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — 4 powers, full toolkit
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Ordonare: 4 puteri — bază 2 cu rebazare",
        "category": "power_order",
        "difficulty": "hard",
        "exercise_type": "drag_order",
        "template": {
            "title": "Ordonare: 4 puteri — bază 2 cu rebazare",
            "type": "drag_order",
            "display_mode": "drag_number",
            "question": "Ordonați crescător numerele:",
            "params": {
                # Effective 2-exponents (strictly disjoint):
                #   2^e1    →    e1  ∈ [25, 35]
                #   4^e2    →  2·e2  ∈ [40, 50]   (e2 ∈ [20, 25])
                #   8^e3    →  3·e3  ∈ [54, 66]   (e3 ∈ [18, 22])
                #   16^e4   →  4·e4  ∈ [72, 88]   (e4 ∈ [18, 22])
                "e1": {"type": "randint", "min": 25, "max": 35},
                "e2": {"type": "randint", "min": 20, "max": 25},
                "e3": {"type": "randint", "min": 18, "max": 22},
                "e4": {"type": "randint", "min": 18, "max": 22},
            },
            "items": ["2**{e1}", "4**{e2}", "8**{e3}", "16**{e4}"],
            "order_direction": "ascending",
        },
    },
    {
        "name": "Ordonare: 4 puteri ale lui 3 cu rebazare",
        "category": "power_order",
        "difficulty": "hard",
        "exercise_type": "drag_order",
        "template": {
            "title": "Ordonare: 4 puteri ale lui 3 cu rebazare",
            "type": "drag_order",
            "display_mode": "drag_number",
            "question": "Ordonați crescător numerele:",
            "params": {
                # Effective 3-exponents (strictly disjoint):
                #   3^e1    →    e1  ∈ [20, 30]
                #   9^e2    →  2·e2  ∈ [34, 44]   (e2 ∈ [17, 22])
                #   27^e3   →  3·e3  ∈ [48, 60]   (e3 ∈ [16, 20])
                #   81^e4   →  4·e4  ∈ [64, 80]   (e4 ∈ [16, 20])
                "e1": {"type": "randint", "min": 20, "max": 30},
                "e2": {"type": "randint", "min": 17, "max": 22},
                "e3": {"type": "randint", "min": 16, "max": 20},
                "e4": {"type": "randint", "min": 16, "max": 20},
            },
            "items": ["3**{e1}", "9**{e2}", "27**{e3}", "81**{e4}"],
            "order_direction": "ascending",
        },
    },
    {
        "name": "Ordonare: baze și exponenți diferiți (estimare prin log)",
        "category": "power_order",
        "difficulty": "hard",
        "exercise_type": "drag_order",
        "template": {
            "title": "Ordonare: baze și exponenți diferiți (estimare prin log)",
            "type": "drag_order",
            "display_mode": "drag_number",
            "question": "Ordonați crescător numerele:",
            "params": {
                # Approximate log10 magnitudes:
                #   10^(k+5):   k + 5
                #   3^(3k+6):   (3k+6) · 0.477 ≈ 1.431·k + 2.862
                #   2^(5k+15):  (5k+15) · 0.301 ≈ 1.505·k + 4.515
                #
                # For k ∈ [8, 16] the order is consistent:
                #   10^(k+5)  <  3^(3k+6)  <  2^(5k+15)
                # with log10 gaps > 1 so no numerical ties.
                "k":  {"type": "randint", "min": 8, "max": 16},
                "x1": {"type": "computed", "expr": "{k} + 5"},
                "x2": {"type": "computed", "expr": "5 * {k} + 15"},
                "x3": {"type": "computed", "expr": "3 * {k} + 6"},
            },
            "items": ["10**{x1}", "2**{x2}", "3**{x3}"],
            "order_direction": "ascending",
        },
    },
]
