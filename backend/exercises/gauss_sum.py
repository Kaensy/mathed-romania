"""
Exercise data: gauss_sum
Topic 1.4 — Adunarea numerelor naturale

Category: gauss_sum
Label (RO): Suma lui Gauss

Tiers:
  Easy   — Basic Gauss sums: 1+2+...+n, multiples, consecutive range
  Medium — Larger ranges, arithmetic series sums with step
  Hard   — Inverse: find consecutive numbers given their sum

Usage:
    python manage.py load_exercises exercises.gauss_sum
    python manage.py load_exercises exercises.gauss_sum --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 4,
}

EXERCISES = [

    # ── EASY ─────────────────────────────────────────────────────────────────

    {
        "name": "Gauss: 1 + 2 + ... + n",
        "category": "gauss_sum",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Gauss: 1 + 2 + ... + n",
            "type": "fill_blank",
            "question": "Calculați suma:  $1 + 2 + 3 + \\ldots + {n}$",
            "params": {
                "n":   {"type": "randint", "min": 5, "max": 30},
                "ans": {"type": "computed", "expr": "{n} * ({n} + 1) // 2"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Folosiți formula lui Gauss: $S = \\frac{{n \\cdot (n+1)}}{{2}}$, unde $n = {n}$.",
            "placeholder": "S = ?",
        },
    },
    {
        "name": "Gauss: 10 + 20 + ... + n (multipli de 10)",
        "category": "gauss_sum",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Gauss: 10 + 20 + ... + n (multipli de 10)",
            "type": "fill_blank",
            "question": "Calculați suma:  $10 + 20 + 30 + \\ldots + {last}$",
            "params": {
                "k":    {"type": "randint", "min": 5, "max": 15},
                "last": {"type": "computed", "expr": "{k} * 10"},
                "ans":  {"type": "computed", "expr": "10 * {k} * ({k} + 1) // 2"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Observați: $10 + 20 + \\ldots + {last} = 10 \\cdot (1 + 2 + \\ldots + {k})$. Aplicați formula lui Gauss.",
            "placeholder": "S = ?",
        },
    },
    {
        "name": "Gauss: multipli de d",
        "category": "gauss_sum",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Gauss: multipli de d",
            "type": "fill_blank",
            "question": "Calculați suma:  ${d} + {t2} + {t3} + \\ldots + {last}$",
            "params": {
                "d":    {"type": "randint", "min": 3, "max": 9},
                "k":    {"type": "randint", "min": 5, "max": 12},
                "t2":   {"type": "computed", "expr": "2 * {d}"},
                "t3":   {"type": "computed", "expr": "3 * {d}"},
                "last": {"type": "computed", "expr": "{k} * {d}"},
                "ans":  {"type": "computed", "expr": "{d} * {k} * ({k} + 1) // 2"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Observați: ${d} + {t2} + \\ldots + {last} = {d} \\cdot (1 + 2 + \\ldots + {k})$.",
            "placeholder": "S = ?",
        },
    },
    {
        "name": "Gauss: sumă de la a la b",
        "category": "gauss_sum",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Gauss: sumă de la a la b",
            "type": "fill_blank",
            "question": "Calculați suma:  ${a} + {a1} + {a2} + \\ldots + {b}$",
            "params": {
                "a":     {"type": "randint", "min": 5, "max": 30},
                "count": {"type": "randint", "min": 5, "max": 20},
                "b":     {"type": "computed", "expr": "{a} + {count} - 1"},
                "a1":    {"type": "computed", "expr": "{a} + 1"},
                "a2":    {"type": "computed", "expr": "{a} + 2"},
                "ans":   {"type": "computed", "expr": "{count} * ({a} + {b}) // 2"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "De la ${a}$ la ${b}$ sunt ${count}$ termeni. $S = \\frac{{{count} \\cdot ({a} + {b})}}{{2}}$.",
            "placeholder": "S = ?",
        },
    },

    # ── MEDIUM ───────────────────────────────────────────────────────────────

    {
        "name": "Gauss: sumă interval mare",
        "category": "gauss_sum",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Gauss: sumă interval mare",
            "type": "fill_blank",
            "question": "Calculați suma:  ${a} + {a1} + {a2} + \\ldots + {b}$",
            "params": {
                "a":     {"type": "randint", "min": 50, "max": 200},
                "count": {"type": "randint", "min": 20, "max": 80},
                "b":     {"type": "computed", "expr": "{a} + {count} - 1"},
                "a1":    {"type": "computed", "expr": "{a} + 1"},
                "a2":    {"type": "computed", "expr": "{a} + 2"},
                "ans":   {"type": "computed", "expr": "{count} * ({a} + {b}) // 2"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "De la ${a}$ la ${b}$ sunt ${count}$ termeni. $S = \\frac{{{count} \\cdot ({a} + {b})}}{{2}}$.",
            "placeholder": "S = ?",
        },
    },
    {
        "name": "Gauss: sumă serie aritmetică cu rație",
        "category": "gauss_sum",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Gauss: sumă serie aritmetică cu rație",
            "type": "fill_blank",
            "question": "Calculați suma:  ${a1} + {a2} + {a3} + \\ldots + {last}$",
            "params": {
                "a1":   {"type": "randint", "min": 2, "max": 20},
                "d":    {"type": "randint", "min": 2, "max": 8},
                "n":    {"type": "randint", "min": 8, "max": 20},
                "a2":   {"type": "computed", "expr": "{a1} + {d}"},
                "a3":   {"type": "computed", "expr": "{a1} + 2 * {d}"},
                "last": {"type": "computed", "expr": "{a1} + ({n} - 1) * {d}"},
                "ans":  {"type": "computed", "expr": "{n} * ({a1} + {last}) // 2"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Rația este ${d}$, ultimul termen este ${last}$. Sunt ${n}$ termeni. $S = \\frac{{{n} \\cdot ({a1} + {last})}}{{2}}$.",
            "placeholder": "S = ?",
        },
    },
    {
        "name": "Gauss: 1+2+...+b minus 1+2+...+a",
        "category": "gauss_sum",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Gauss: diferența a două sume Gauss",
            "type": "fill_blank",
            "question": "Calculați:  $(1 + 2 + \\ldots + {b}) - (1 + 2 + \\ldots + {a})$",
            "params": {
                "a":    {"type": "randint", "min": 5, "max": 30},
                "b":    {"type": "randint", "min": 40, "max": 100},
                "sum_b": {"type": "computed", "expr": "{b} * ({b} + 1) // 2"},
                "sum_a": {"type": "computed", "expr": "{a} * ({a} + 1) // 2"},
                "ans":   {"type": "computed", "expr": "{sum_b} - {sum_a}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Calculați fiecare sumă separat: $1+2+\\ldots+{b} = {sum_b}$ și $1+2+\\ldots+{a} = {sum_a}$.",
            "placeholder": "= ?",
        },
    },

    # ── HARD ─────────────────────────────────────────────────────────────────

    {
        "name": "Consecutive: suma a 3 numere consecutive",
        "category": "gauss_sum",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Consecutive: suma a 3 numere consecutive",
            "type": "fill_blank",
            "question": "Suma a 3 numere naturale consecutive este ${sum}$. Determinați numărul din mijloc.",
            "params": {
                "mid": {"type": "randint", "min": 20, "max": 500},
                "sum": {"type": "computed", "expr": "3 * {mid}"},
            },
            "answer_expr": "{mid}",
            "answer_input": "number",
            "hint": "Dacă cele 3 numere consecutive sunt $n-1$, $n$, $n+1$, atunci suma lor este $3n$. Deci $n = {sum} : 3$.",
            "placeholder": "Numărul din mijloc = ?",
        },
    },
    {
        "name": "Consecutive: suma a 5 numere consecutive",
        "category": "gauss_sum",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Consecutive: suma a 5 numere consecutive",
            "type": "fill_blank",
            "question": "Suma a 5 numere naturale consecutive este ${sum}$. Determinați cel mai mic dintre ele.",
            "params": {
                "first": {"type": "randint", "min": 20, "max": 300},
                "mid":   {"type": "computed", "expr": "{first} + 2"},
                "sum":   {"type": "computed", "expr": "5 * {mid}"},
            },
            "answer_expr": "{first}",
            "answer_input": "number",
            "hint": "Numărul din mijloc este ${sum} : 5 = {mid}$. Cel mai mic este cu 2 mai puțin: ${mid} - 2$.",
            "placeholder": "Cel mai mic = ?",
        },
    },
    {
        "name": "Consecutive pare: suma a 3 numere pare consecutive",
        "category": "gauss_sum",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Consecutive pare: suma a 3 numere pare consecutive",
            "type": "fill_blank",
            "question": "Suma a 3 numere naturale pare consecutive este ${sum}$. Determinați numărul din mijloc.",
            "params": {
                "mid_half": {"type": "randint", "min": 10, "max": 200},
                "mid":      {"type": "computed", "expr": "2 * {mid_half}"},
                "sum":      {"type": "computed", "expr": "3 * {mid}"},
            },
            "answer_expr": "{mid}",
            "answer_input": "number",
            "hint": "Dacă cele 3 numere pare consecutive sunt $n-2$, $n$, $n+2$, atunci suma lor este $3n$. Deci $n = {sum} : 3$.",
            "placeholder": "Numărul din mijloc = ?",
        },
    },
]
