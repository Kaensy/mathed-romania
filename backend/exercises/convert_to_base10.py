"""
Exercise data: convert_to_base10
Topic 1.9 — Baze de numerație: scrierea în baza 10 și baza 2

Category: convert_to_base10
Label (RO): Conversie spre baza 10

Tiers:
  Easy   — Base-10 expanded-form decomposition:
             724 = 7·100 + 2·10 + 4  (student gives the digits)
           This is place value as a warm-up — conceptually the same as
           conversion (just with source base = target base).
  Medium — Other-base → base 10, small bases and short numbers:
             base 2: 11₍₂₎, 1101₍₂₎
             base 3: 1201₍₃₎
             base 5: 4201₍₅₎
  Hard   — Other-base → base 10 for larger/mixed bases:
             base 6-9, 4-5 digit source numbers
             yielding base-10 values up to ~6 digits

Design notes:
  - Easy uses multi_fill_blank where student supplies each digit of the
    decomposition in sequence (matching textbook Ex 1's presentation).
  - Medium and Hard use fill_blank with a single number answer.
  - Question strings use `{n}_{{(base)}}` → KaTeX renders as `n₍ᵦₐₛₑ₎`.
  - Source digits generated digit-by-digit to guarantee valid base-b
    representations (no leading zeros, all digits < base).

Usage:
    python manage.py load_exercises exercises.convert_to_base10
    python manage.py load_exercises exercises.convert_to_base10 --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 9,  # "Baze de numerație"
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Base-10 expanded-form decomposition
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Descompunere baza 10: număr de 3 cifre",
        "category": "convert_to_base10",
        "difficulty": "easy",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Descompunere baza 10: număr de 3 cifre",
            "type": "multi_fill_blank",
            "question": "Completați cifrele lipsă din descompunerea numărului ${n}$:  ${n} = a \\cdot 100 + b \\cdot 10 + c$",
            "params": {
                "a": {"type": "randint", "min": 1, "max": 9},
                "b": {"type": "randint", "min": 0, "max": 9},
                "c": {"type": "randint", "min": 0, "max": 9},
                "n": {"type": "computed", "expr": "{a} * 100 + {b} * 10 + {c}"},
            },
            "fields": [
                {"key": "a", "label": "a", "answer_expr": "{a}"},
                {"key": "b", "label": "b", "answer_expr": "{b}"},
                {"key": "c", "label": "c", "answer_expr": "{c}"},
            ],
            "answer_input": "number",
            "hint": "Fiecare cifră reprezintă un ordin: sutele, zecile, unitățile.",
        },
    },
    {
        "name": "Descompunere baza 10: număr de 4 cifre",
        "category": "convert_to_base10",
        "difficulty": "easy",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Descompunere baza 10: număr de 4 cifre",
            "type": "multi_fill_blank",
            "question": "Completați cifrele lipsă din descompunerea numărului ${n}$:  ${n} = a \\cdot 10^3 + b \\cdot 10^2 + c \\cdot 10 + d$",
            "params": {
                "a": {"type": "randint", "min": 1, "max": 9},
                "b": {"type": "randint", "min": 0, "max": 9},
                "c": {"type": "randint", "min": 0, "max": 9},
                "d": {"type": "randint", "min": 0, "max": 9},
                "n": {"type": "computed", "expr": "{a} * 1000 + {b} * 100 + {c} * 10 + {d}"},
            },
            "fields": [
                {"key": "a", "label": "a", "answer_expr": "{a}"},
                {"key": "b", "label": "b", "answer_expr": "{b}"},
                {"key": "c", "label": "c", "answer_expr": "{c}"},
                {"key": "d", "label": "d", "answer_expr": "{d}"},
            ],
            "answer_input": "number",
            "hint": "Fiecare cifră reprezintă un ordin: miile, sutele, zecile, unitățile.",
        },
    },
    {
        "name": "Valoarea formei desfășurate (3 termeni)",
        "category": "convert_to_base10",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Valoarea formei desfășurate (3 termeni)",
            "type": "fill_blank",
            "question": "Calculați valoarea formei desfășurate:  ${a} \\cdot 10^2 + {b} \\cdot 10 + {c}$",
            "params": {
                "a":   {"type": "randint", "min": 1, "max": 9},
                "b":   {"type": "randint", "min": 0, "max": 9},
                "c":   {"type": "randint", "min": 0, "max": 9},
                "ans": {"type": "computed", "expr": "{a} * 100 + {b} * 10 + {c}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "$10^2 = 100$. Înmulțiți fiecare cifră cu puterea corespunzătoare și adunați.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Other-base → base 10, small bases
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Conversie bază 2 → bază 10 (număr de 4 cifre)",
        "category": "convert_to_base10",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Conversie bază 2 → bază 10 (număr de 4 cifre)",
            "type": "fill_blank",
            "question": "Scrieți în baza 10 numărul:  $\\overline{{{d3}{d2}{d1}{d0}}}_{{(2)}}$",
            "params": {
                "d3":  {"type": "fixed", "value": 1},
                "d2":  {"type": "randint", "min": 0, "max": 1},
                "d1":  {"type": "randint", "min": 0, "max": 1},
                "d0":  {"type": "randint", "min": 0, "max": 1},
                "ans": {"type": "computed", "expr": "{d3} * 8 + {d2} * 4 + {d1} * 2 + {d0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "În baza 2: $\\overline{{abcd}}_{{(2)}} = a \\cdot 2^3 + b \\cdot 2^2 + c \\cdot 2 + d$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Conversie bază 2 → bază 10 (număr de 6 cifre)",
        "category": "convert_to_base10",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Conversie bază 2 → bază 10 (număr de 6 cifre)",
            "type": "fill_blank",
            "question": "Scrieți în baza 10 numărul:  $\\overline{{{d5}{d4}{d3}{d2}{d1}{d0}}}_{{(2)}}$",
            "params": {
                "d5":  {"type": "fixed", "value": 1},
                "d4":  {"type": "randint", "min": 0, "max": 1},
                "d3":  {"type": "randint", "min": 0, "max": 1},
                "d2":  {"type": "randint", "min": 0, "max": 1},
                "d1":  {"type": "randint", "min": 0, "max": 1},
                "d0":  {"type": "randint", "min": 0, "max": 1},
                "ans": {"type": "computed", "expr": "{d5} * 32 + {d4} * 16 + {d3} * 8 + {d2} * 4 + {d1} * 2 + {d0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Puterile lui 2: $2^5 = 32$, $2^4 = 16$, $2^3 = 8$, $2^2 = 4$, $2 = 2$, $1$. Înmulțiți fiecare cifră cu puterea corespunzătoare și adunați.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Conversie bază 3 → bază 10",
        "category": "convert_to_base10",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Conversie bază 3 → bază 10",
            "type": "fill_blank",
            "question": "Scrieți în baza 10 numărul:  $\\overline{{{d3}{d2}{d1}{d0}}}_{{(3)}}$",
            "params": {
                "d3":  {"type": "randint", "min": 1, "max": 2},
                "d2":  {"type": "randint", "min": 0, "max": 2},
                "d1":  {"type": "randint", "min": 0, "max": 2},
                "d0":  {"type": "randint", "min": 0, "max": 2},
                "ans": {"type": "computed", "expr": "{d3} * 27 + {d2} * 9 + {d1} * 3 + {d0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Puterile lui 3: $3^3 = 27$, $3^2 = 9$, $3 = 3$, $1$. În baza 3, cifrele pot fi doar $0$, $1$ sau $2$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Conversie bază 5 → bază 10",
        "category": "convert_to_base10",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Conversie bază 5 → bază 10",
            "type": "fill_blank",
            "question": "Scrieți în baza 10 numărul:  $\\overline{{{d3}{d2}{d1}{d0}}}_{{(5)}}$",
            "params": {
                "d3":  {"type": "randint", "min": 1, "max": 4},
                "d2":  {"type": "randint", "min": 0, "max": 4},
                "d1":  {"type": "randint", "min": 0, "max": 4},
                "d0":  {"type": "randint", "min": 0, "max": 4},
                "ans": {"type": "computed", "expr": "{d3} * 125 + {d2} * 25 + {d1} * 5 + {d0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Puterile lui 5: $5^3 = 125$, $5^2 = 25$, $5 = 5$, $1$. În baza 5, cifrele pot fi $0, 1, 2, 3, 4$.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Other-base → base 10, bases 6-9 or longer numbers
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Conversie bază 6 → bază 10 (5 cifre)",
        "category": "convert_to_base10",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Conversie bază 6 → bază 10 (5 cifre)",
            "type": "fill_blank",
            "question": "Scrieți în baza 10 numărul:  $\\overline{{{d4}{d3}{d2}{d1}{d0}}}_{{(6)}}$",
            "params": {
                "d4":  {"type": "randint", "min": 1, "max": 5},
                "d3":  {"type": "randint", "min": 0, "max": 5},
                "d2":  {"type": "randint", "min": 0, "max": 5},
                "d1":  {"type": "randint", "min": 0, "max": 5},
                "d0":  {"type": "randint", "min": 0, "max": 5},
                "ans": {"type": "computed", "expr": "{d4} * 1296 + {d3} * 216 + {d2} * 36 + {d1} * 6 + {d0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Puterile lui 6: $6^4 = 1296$, $6^3 = 216$, $6^2 = 36$, $6 = 6$, $1$. În baza 6, cifrele pot fi $0, 1, 2, 3, 4, 5$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Conversie bază 8 → bază 10 (4 cifre)",
        "category": "convert_to_base10",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Conversie bază 8 → bază 10 (4 cifre)",
            "type": "fill_blank",
            "question": "Scrieți în baza 10 numărul:  $\\overline{{{d3}{d2}{d1}{d0}}}_{{(8)}}$",
            "params": {
                "d3":  {"type": "randint", "min": 1, "max": 7},
                "d2":  {"type": "randint", "min": 0, "max": 7},
                "d1":  {"type": "randint", "min": 0, "max": 7},
                "d0":  {"type": "randint", "min": 0, "max": 7},
                "ans": {"type": "computed", "expr": "{d3} * 512 + {d2} * 64 + {d1} * 8 + {d0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Puterile lui 8: $8^3 = 512$, $8^2 = 64$, $8 = 8$, $1$. În baza 8, cifrele pot fi $0, 1, \\ldots, 7$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Conversie bază 9 → bază 10 (4 cifre)",
        "category": "convert_to_base10",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Conversie bază 9 → bază 10 (4 cifre)",
            "type": "fill_blank",
            "question": "Scrieți în baza 10 numărul:  $\\overline{{{d3}{d2}{d1}{d0}}}_{{(9)}}$",
            "params": {
                "d3":  {"type": "randint", "min": 1, "max": 8},
                "d2":  {"type": "randint", "min": 0, "max": 8},
                "d1":  {"type": "randint", "min": 0, "max": 8},
                "d0":  {"type": "randint", "min": 0, "max": 8},
                "ans": {"type": "computed", "expr": "{d3} * 729 + {d2} * 81 + {d1} * 9 + {d0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Puterile lui 9: $9^3 = 729$, $9^2 = 81$, $9 = 9$, $1$. În baza 9, cifrele pot fi $0, 1, \\ldots, 8$.",
            "placeholder": "= ?",
        },
    },
]
