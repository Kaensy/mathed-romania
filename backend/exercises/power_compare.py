"""
Exercise data: power_compare
Topic 1.8 — Puterea cu exponent natural (sub-lesson C: comparare, pătrate)

Category: power_compare
Label (RO): Compararea puterilor

Tiers:
  Easy   — Direct comparison:
             same base, different exponents    (m < n ⇒ a^m < a^n, a > 1)
             same exponent, different bases    (a < b ⇒ a^n < b^n)
             mixed with conventions (1^n, a^0, (a+b)^0 etc.)
  Medium — One-step rebasing:
             compare a^m vs b^n where b is a power of a (or vice versa)
             reduce to same-base case
  Hard   — Two-step: bring to same exponent OR use intermediary:
             compare via (a^p)^k vs (b^q)^k → same exponent k
             compare via common intermediary power

Design notes:
  - Uses the engine's `comparison` exercise type (renders <, =, > buttons).
  - `left` and `right` are Python expressions evaluated by the engine,
    then compared. The actual string displayed to the student is the
    raw template string with {params} substituted — so we want to show
    the *original* unsimplified form.
  - Python ** works on arbitrary integers so all comparisons resolve
    exactly, even for huge exponents.

Usage:
    python manage.py load_exercises exercises.power_compare
    python manage.py load_exercises exercises.power_compare --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 8,
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Direct comparison
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Aceeași bază, exponenți diferiți",
        "category": "power_compare",
        "difficulty": "easy",
        "exercise_type": "comparison",
        "template": {
            "title": "Aceeași bază, exponenți diferiți",
            "type": "comparison",
            "question": "Comparați numerele:",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 20},
                "m": {"type": "randint", "min": 20, "max": 100},
                "n": {"type": "randint", "min": 101, "max": 200},
            },
            "left":  "{a}**{m}",
            "right": "{a}**{n}",
        },
    },
    {
        "name": "Același exponent, baze diferite",
        "category": "power_compare",
        "difficulty": "easy",
        "exercise_type": "comparison",
        "template": {
            "title": "Același exponent, baze diferite",
            "type": "comparison",
            "question": "Comparați numerele:",
            "params": {
                "a": {"type": "randint", "min": 2, "max": 50},
                "b": {"type": "randint", "min": 51, "max": 200},
                "n": {"type": "randint", "min": 20, "max": 100},
            },
            "left":  "{a}**{n}",
            "right": "{b}**{n}",
        },
    },
    {
        "name": "Cu convenții: a^0 sau 1^n",
        "category": "power_compare",
        "difficulty": "easy",
        "exercise_type": "comparison",
        "template": {
            "title": "Cu convenții: a^0 sau 1^n",
            "type": "comparison",
            "question": "Comparați numerele:",
            "params": {
                # Left: a^0 = 1 for any nonzero a.
                # Right: 1^n = 1 for any n.
                # Result is always equality.
                "a": {"type": "randint", "min": 2, "max": 9999},
                "n": {"type": "randint", "min": 2, "max": 200},
            },
            "left":  "{a}**0",
            "right": "1**{n}",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — One-step rebasing
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Rebazare: 2^m vs 4^n",
        "category": "power_compare",
        "difficulty": "medium",
        "exercise_type": "comparison",
        "template": {
            "title": "Rebazare: 2^m vs 4^n",
            "type": "comparison",
            "question": "Comparați numerele:",
            "params": {
                "m": {"type": "randint", "min": 20, "max": 200},
                "n": {"type": "randint", "min": 10, "max": 100},
            },
            "left":  "2**{m}",
            "right": "4**{n}",
        },
    },
    {
        "name": "Rebazare: 3^m vs 9^n",
        "category": "power_compare",
        "difficulty": "medium",
        "exercise_type": "comparison",
        "template": {
            "title": "Rebazare: 3^m vs 9^n",
            "type": "comparison",
            "question": "Comparați numerele:",
            "params": {
                "m": {"type": "randint", "min": 20, "max": 200},
                "n": {"type": "randint", "min": 10, "max": 100},
            },
            "left":  "3**{m}",
            "right": "9**{n}",
        },
    },
    {
        "name": "Rebazare: 2^m vs 8^n",
        "category": "power_compare",
        "difficulty": "medium",
        "exercise_type": "comparison",
        "template": {
            "title": "Rebazare: 2^m vs 8^n",
            "type": "comparison",
            "question": "Comparați numerele:",
            "params": {
                "m": {"type": "randint", "min": 30, "max": 300},
                "n": {"type": "randint", "min": 10, "max": 100},
            },
            "left":  "2**{m}",
            "right": "8**{n}",
        },
    },
    {
        "name": "Rebazare: 5^m vs 25^n",
        "category": "power_compare",
        "difficulty": "medium",
        "exercise_type": "comparison",
        "template": {
            "title": "Rebazare: 5^m vs 25^n",
            "type": "comparison",
            "question": "Comparați numerele:",
            "params": {
                "m": {"type": "randint", "min": 20, "max": 200},
                "n": {"type": "randint", "min": 10, "max": 100},
            },
            "left":  "5**{m}",
            "right": "25**{n}",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Reduce to same exponent (different bases, different exponents)
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Același exponent țintă: a^(k·p) vs b^(k·q)",
        "category": "power_compare",
        "difficulty": "hard",
        "exercise_type": "comparison",
        "template": {
            "title": "Același exponent țintă: a^(k·p) vs b^(k·q)",
            "type": "comparison",
            "question": "Comparați numerele:",
            "params": {
                # Structured so both can be rewritten as (something)^k.
                # Student: observe common factor in both exponents, rewrite.
                "a":  {"type": "choice", "options": [2, 3, 5, 7]},
                "b":  {"type": "choice", "options": [2, 3, 5, 7]},
                "k":  {"type": "randint", "min": 5, "max": 15},
                "p":  {"type": "randint", "min": 2, "max": 5},
                "q":  {"type": "randint", "min": 2, "max": 5},
                "m":  {"type": "computed", "expr": "{k} * {p}"},
                "n":  {"type": "computed", "expr": "{k} * {q}"},
            },
            "left":  "{a}**{m}",
            "right": "{b}**{n}",
        },
    },
    {
        "name": "Intermediar prin inegalitate de baze (2^3 < 3^2)",
        "category": "power_compare",
        "difficulty": "hard",
        "exercise_type": "comparison",
        "template": {
            "title": "Intermediar: 8 < 9 deci 2^(3k) < 3^(2k)",
            "type": "comparison",
            "question": "Comparați numerele:",
            "params": {
                # Pattern: 2^(3k) vs 3^(2k). Since 2^3 = 8 < 9 = 3^2,
                # we have (2^3)^k < (3^2)^k, i.e. 2^(3k) < 3^(2k).
                "k": {"type": "randint", "min": 10, "max": 50},
                "m": {"type": "computed", "expr": "3 * {k}"},
                "n": {"type": "computed", "expr": "2 * {k}"},
            },
            "left":  "2**{m}",
            "right": "3**{n}",
        },
    },
    {
        "name": "Intermediar prin 5^2 < 3^3 (25 < 27)",
        "category": "power_compare",
        "difficulty": "hard",
        "exercise_type": "comparison",
        "template": {
            "title": "Intermediar: 25 < 27 deci 5^(2k) < 3^(3k)",
            "type": "comparison",
            "question": "Comparați numerele:",
            "params": {
                "k": {"type": "randint", "min": 10, "max": 50},
                "m": {"type": "computed", "expr": "2 * {k}"},
                "n": {"type": "computed", "expr": "3 * {k}"},
            },
            "left":  "5**{m}",
            "right": "3**{n}",
        },
    },
    {
        "name": "Sumă vs putere singură: 2^(n+1) + 2^n vs 3 · 2^n",
        "category": "power_compare",
        "difficulty": "hard",
        "exercise_type": "comparison",
        "template": {
            "title": "Sumă vs putere singură: 2^(n+1) + 2^n vs 3 · 2^n",
            "type": "comparison",
            "question": "Comparați numerele:",
            "params": {
                # 2^(n+1) + 2^n = 2 · 2^n + 2^n = 3 · 2^n. Equal.
                # Tests factor-comun skill in comparison form.
                "n":  {"type": "randint", "min": 10, "max": 100},
                "n1": {"type": "computed", "expr": "{n} + 1"},
            },
            "left":  "2**{n1} + 2**{n}",
            "right": "3 * 2**{n}",
        },
    },
]
