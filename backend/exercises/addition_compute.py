"""
Exercise data: addition_compute
Topic 1.4 — Adunarea numerelor naturale

Category: addition_compute
Label (RO): Calcul cu adunări

Tiers:
  Easy   — Direct computation (2-4 terms, 3-5 digit numbers)
  Medium — Large numbers + clever grouping (pairs to 100/1000)
  Hard   — Last digit of a sum (modulo 10 trick)

Usage:
    python manage.py load_exercises exercises.addition_compute
    python manage.py load_exercises exercises.addition_compute --flush   # replace existing
    python manage.py load_exercises exercises.addition_compute --dry-run # preview only
"""

# ═══════════════════════════════════════════════════════════════════════════════
# TOPIC REFERENCE — adjust if your topic order differs!
#
# Check your DB:  Topic.objects.filter(unit__grade__number=5, unit__order=1)
# Or in admin:    /admin/content/topic/?unit__grade__number=5&unit__order=1
# ═══════════════════════════════════════════════════════════════════════════════

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 4,  # "Adunarea numerelor naturale" (id=4)
}


# ═══════════════════════════════════════════════════════════════════════════════
# EXERCISES
# ═══════════════════════════════════════════════════════════════════════════════

EXERCISES = [

    # ── EASY: Direct computation ─────────────────────────────────────────────

    {
        "name": "Adunare: două numere de 3 cifre",
        "category": "addition_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Adunare: două numere de 3 cifre",
            "type": "fill_blank",
            "question": "Calculați:  ${a} + {b}$",
            "params": {
                "a": {"type": "randint", "min": 100, "max": 999},
                "b": {"type": "randint", "min": 100, "max": 999},
            },
            "answer_expr": "{a} + {b}",
            "answer_input": "number",
            "hint": "Adunați cele două numere.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Adunare: două numere de 4-5 cifre",
        "category": "addition_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Adunare: două numere de 4-5 cifre",
            "type": "fill_blank",
            "question": "Calculați:  ${a} + {b}$",
            "params": {
                "a": {"type": "randint", "min": 1000, "max": 99999},
                "b": {"type": "randint", "min": 1000, "max": 99999},
            },
            "answer_expr": "{a} + {b}",
            "answer_input": "number",
            "hint": "Adunați cele două numere.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Adunare: trei termeni",
        "category": "addition_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Adunare: trei termeni",
            "type": "fill_blank",
            "question": "Calculați:  ${a} + {b} + {c}$",
            "params": {
                "a": {"type": "randint", "min": 100, "max": 9999},
                "b": {"type": "randint", "min": 100, "max": 9999},
                "c": {"type": "randint", "min": 100, "max": 9999},
            },
            "answer_expr": "{a} + {b} + {c}",
            "answer_input": "number",
            "hint": "Adunați numerele pe rând, de la stânga la dreapta.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Adunare: patru termeni",
        "category": "addition_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Adunare: patru termeni",
            "type": "fill_blank",
            "question": "Calculați:  ${a} + {b} + {c} + {d}$",
            "params": {
                "a": {"type": "randint", "min": 100, "max": 5000},
                "b": {"type": "randint", "min": 100, "max": 5000},
                "c": {"type": "randint", "min": 100, "max": 5000},
                "d": {"type": "randint", "min": 100, "max": 5000},
            },
            "answer_expr": "{a} + {b} + {c} + {d}",
            "answer_input": "number",
            "hint": "Adunați numerele pe rând.",
            "placeholder": "= ?",
        },
    },

    # ── MEDIUM: Large numbers + clever grouping ──────────────────────────────

    {
        "name": "Adunare: trei numere mari (5-6 cifre)",
        "category": "addition_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Adunare: trei numere mari (5-6 cifre)",
            "type": "fill_blank",
            "question": "Calculați:  ${a} + {b} + {c}$",
            "params": {
                "a": {"type": "randint", "min": 10000, "max": 999999},
                "b": {"type": "randint", "min": 10000, "max": 999999},
                "c": {"type": "randint", "min": 100, "max": 9999},
            },
            "answer_expr": "{a} + {b} + {c}",
            "answer_input": "number",
            "hint": "Adunați numerele pe rând. Aveți grijă la transport!",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Adunare: patru numere mari",
        "category": "addition_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Adunare: patru numere mari",
            "type": "fill_blank",
            "question": "Calculați:  ${a} + {b} + {c} + {d}$",
            "params": {
                "a": {"type": "randint", "min": 10000, "max": 500000},
                "b": {"type": "randint", "min": 10000, "max": 500000},
                "c": {"type": "randint", "min": 1000, "max": 99999},
                "d": {"type": "randint", "min": 100, "max": 9999},
            },
            "answer_expr": "{a} + {b} + {c} + {d}",
            "answer_input": "number",
            "hint": "Adunați numerele pe rând, de la stânga la dreapta.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Grupare inteligentă: perechi cu suma 100",
        "category": "addition_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Grupare inteligentă: perechi cu suma 100",
            "type": "fill_blank",
            "question": "Folosind proprietățile adunării, calculați:  $S = {a1} + {b2} + {a3} + {extra} + {a2} + {b3} + {b1}$",
            "params": {
                "a1":    {"type": "randint", "min": 11, "max": 28},
                "a2":    {"type": "randint", "min": 32, "max": 43},
                "a3":    {"type": "randint", "min": 45, "max": 49},
                "b1":    {"type": "computed", "expr": "100 - {a1}"},
                "b2":    {"type": "computed", "expr": "100 - {a2}"},
                "b3":    {"type": "computed", "expr": "100 - {a3}"},
                "extra": {"type": "randint", "min": 100, "max": 400},
            },
            "answer_expr": "{a1} + {b1} + {a2} + {b2} + {a3} + {b3} + {extra}",
            "answer_input": "number",
            "hint": "Căutați perechile de numere a căror sumă este $100$: ${a1} + {b1}$, ${a2} + {b2}$, ${a3} + {b3}$.",
            "placeholder": "S = ?",
        },
    },
    {
        "name": "Grupare inteligentă: perechi cu suma 1000",
        "category": "addition_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Grupare inteligentă: perechi cu suma 1000",
            "type": "fill_blank",
            "question": "Folosind proprietățile adunării, calculați:  $S = {a2} + {b1} + {a3} + {extra} + {b3} + {a1} + {b2}$",
            "params": {
                "a1":    {"type": "randint", "min": 110, "max": 280},
                "a2":    {"type": "randint", "min": 320, "max": 440},
                "a3":    {"type": "randint", "min": 450, "max": 490},
                "b1":    {"type": "computed", "expr": "1000 - {a1}"},
                "b2":    {"type": "computed", "expr": "1000 - {a2}"},
                "b3":    {"type": "computed", "expr": "1000 - {a3}"},
                "extra": {"type": "randint", "min": 100, "max": 2000},
            },
            "answer_expr": "{a1} + {b1} + {a2} + {b2} + {a3} + {b3} + {extra}",
            "answer_input": "number",
            "hint": "Căutați perechile de numere a căror sumă este $1000$: ${a1} + {b1}$, ${a2} + {b2}$, ${a3} + {b3}$.",
            "placeholder": "S = ?",
        },
    },

    # ── HARD: Last digit of a sum ────────────────────────────────────────────

    {
        "name": "Ultima cifră: sumă de 5 numere",
        "category": "addition_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Ultima cifră: sumă de 5 numere",
            "type": "fill_blank",
            "question": "Determinați ultima cifră a sumei:  $S = {a} + {b} + {c} + {d} + {e}$",
            "params": {
                "a":   {"type": "randint", "min": 100, "max": 999},
                "b":   {"type": "randint", "min": 100, "max": 999},
                "c":   {"type": "randint", "min": 100, "max": 999},
                "d":   {"type": "randint", "min": 100, "max": 999},
                "e":   {"type": "randint", "min": 100, "max": 999},
                "ans": {"type": "computed", "expr": "({a} + {b} + {c} + {d} + {e}) % 10"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Nu trebuie să calculați toată suma! Adunați doar cifrele unităților.",
            "placeholder": "Ultima cifră = ?",
        },
    },
    {
        "name": "Ultima cifră: sumă de 7 numere mari",
        "category": "addition_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Ultima cifră: sumă de 7 numere mari",
            "type": "fill_blank",
            "question": "Determinați ultima cifră a sumei:  $S = {a} + {b} + {c} + {d} + {e} + {f} + {g}$",
            "params": {
                "a":   {"type": "randint", "min": 100, "max": 9999},
                "b":   {"type": "randint", "min": 100, "max": 9999},
                "c":   {"type": "randint", "min": 100, "max": 9999},
                "d":   {"type": "randint", "min": 100, "max": 9999},
                "e":   {"type": "randint", "min": 100, "max": 9999},
                "f":   {"type": "randint", "min": 100, "max": 9999},
                "g":   {"type": "randint", "min": 100, "max": 9999},
                "ans": {"type": "computed", "expr": "({a} + {b} + {c} + {d} + {e} + {f} + {g}) % 10"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Adunați doar cifrele unităților fiecărui număr, apoi luați ultima cifră a acelei sume.",
            "placeholder": "Ultima cifră = ?",
        },
    },
    {
        "name": "Ultima cifră: șir aritmetic (6 termeni)",
        "category": "addition_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Ultima cifră: șir aritmetic (6 termeni)",
            "type": "fill_blank",
            "question": "Determinați ultima cifră a sumei:  $S = {t1} + {t2} + {t3} + {t4} + {t5} + {t6}$",
            "params": {
                "start": {"type": "randint", "min": 100, "max": 999},
                "step":  {"type": "randint", "min": 7, "max": 15},
                "t1":    {"type": "computed", "expr": "{start}"},
                "t2":    {"type": "computed", "expr": "{start} + {step}"},
                "t3":    {"type": "computed", "expr": "{start} + 2 * {step}"},
                "t4":    {"type": "computed", "expr": "{start} + 3 * {step}"},
                "t5":    {"type": "computed", "expr": "{start} + 4 * {step}"},
                "t6":    {"type": "computed", "expr": "{start} + 5 * {step}"},
                "ans":   {"type": "computed", "expr": "(6 * {start} + 15 * {step}) % 10"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Observați: numerele formează un șir aritmetic cu rația ${step}$. Adunați doar cifrele unităților.",
            "placeholder": "Ultima cifră = ?",
        },
    },
]