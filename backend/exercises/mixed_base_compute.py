"""
Exercise data: mixed_base_compute
Topic 1.9 — Baze de numerație: scrierea în baza 10 și baza 2

Category: mixed_base_compute
Label (RO): Calcul cu baze diferite

Tiers:
  Easy   — Simple operations between numbers in DIFFERENT bases with
           result in base 10 (no conversion of the result):
             123₍₄₎ + 24₍₅₎ = ?   (answer in base 10)
             1001₍₂₎ + 101₍₂₎ = ? (answer in base 10)
  Medium — Operations where BOTH operands are in the same non-decimal base
           and the RESULT is requested in that same base:
             1011₍₂₎ + 11₍₂₎ = ?₍₂₎
             101₍₂₎ · 101₍₂₎ = ?₍₂₎
  Hard   — Operations across different bases with the result in a specified
           (often smaller) base:
             1102₍₃₎ + 234₍₁₀₎ = ?₍₃₎
             mixed with three-digit operands and subtraction

Design notes:
  - Easy answer is in base 10 → standard fill_blank with numeric answer.
  - Medium/Hard answer is a digit-string in target base → same trick as
    convert_from_base10: student types digits, we grade as decimal integer.
  - All operand generators produce valid base-b digits.
  - Subtraction templates ensure the larger number is first.

Usage:
    python manage.py load_exercises exercises.mixed_base_compute
    python manage.py load_exercises exercises.mixed_base_compute --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 9,
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Result in base 10
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Sumă baze diferite → baza 10: abc₍₄₎ + de₍₅₎",
        "category": "mixed_base_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Sumă baze diferite → baza 10: abc₍₄₎ + de₍₅₎",
            "type": "fill_blank",
            "question": "Calculați, scriind rezultatul în baza 10:  $\\overline{{{a2}{a1}{a0}}}_{{(4)}} + \\overline{{{b1}{b0}}}_{{(5)}}$",
            "params": {
                "a2":    {"type": "randint", "min": 1, "max": 3},
                "a1":    {"type": "randint", "min": 0, "max": 3},
                "a0":    {"type": "randint", "min": 0, "max": 3},
                "b1":    {"type": "randint", "min": 1, "max": 4},
                "b0":    {"type": "randint", "min": 0, "max": 4},
                "val_a": {"type": "computed", "expr": "{a2} * 16 + {a1} * 4 + {a0}"},
                "val_b": {"type": "computed", "expr": "{b1} * 5 + {b0}"},
                "ans":   {"type": "computed", "expr": "{val_a} + {val_b}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Convertiți fiecare număr în baza 10, apoi adunați. $\\overline{{{a2}{a1}{a0}}}_{{(4)}} = {val_a}$ și $\\overline{{{b1}{b0}}}_{{(5)}} = {val_b}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Sumă baza 2 + baza 2 → baza 10",
        "category": "mixed_base_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Sumă baza 2 + baza 2 → baza 10",
            "type": "fill_blank",
            "question": "Calculați, scriind rezultatul în baza 10:  $\\overline{{{a3}{a2}{a1}{a0}}}_{{(2)}} + \\overline{{{b2}{b1}{b0}}}_{{(2)}}$",
            "params": {
                "a3":    {"type": "fixed", "value": 1},
                "a2":    {"type": "randint", "min": 0, "max": 1},
                "a1":    {"type": "randint", "min": 0, "max": 1},
                "a0":    {"type": "randint", "min": 0, "max": 1},
                "b2":    {"type": "fixed", "value": 1},
                "b1":    {"type": "randint", "min": 0, "max": 1},
                "b0":    {"type": "randint", "min": 0, "max": 1},
                "val_a": {"type": "computed", "expr": "{a3} * 8 + {a2} * 4 + {a1} * 2 + {a0}"},
                "val_b": {"type": "computed", "expr": "{b2} * 4 + {b1} * 2 + {b0}"},
                "ans":   {"type": "computed", "expr": "{val_a} + {val_b}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Convertiți cele două numere în baza 10. Puterile lui $2$: $8, 4, 2, 1$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Produs baze diferite → baza 10",
        "category": "mixed_base_compute",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Produs baze diferite → baza 10",
            "type": "fill_blank",
            "question": "Calculați, scriind rezultatul în baza 10:  $\\overline{{{a1}{a0}}}_{{(2)}} \\cdot \\overline{{{b1}{b0}}}_{{(3)}}$",
            "params": {
                "a1":    {"type": "fixed", "value": 1},
                "a0":    {"type": "randint", "min": 0, "max": 1},
                "b1":    {"type": "randint", "min": 1, "max": 2},
                "b0":    {"type": "randint", "min": 0, "max": 2},
                "val_a": {"type": "computed", "expr": "{a1} * 2 + {a0}"},
                "val_b": {"type": "computed", "expr": "{b1} * 3 + {b0}"},
                "ans":   {"type": "computed", "expr": "{val_a} * {val_b}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Convertiți ambele numere în baza 10, apoi înmulțiți.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Result in the same non-decimal base as operands
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Sumă în baza 2 → baza 2",
        "category": "mixed_base_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Sumă în baza 2 → baza 2",
            "type": "fill_blank",
            "question": "Calculați, scriind rezultatul în baza 2:  $\\overline{{{a3}{a2}{a1}{a0}}}_{{(2)}} + \\overline{{{b2}{b1}{b0}}}_{{(2)}}$",
            "params": {
                "a3":    {"type": "fixed", "value": 1},
                "a2":    {"type": "randint", "min": 0, "max": 1},
                "a1":    {"type": "randint", "min": 0, "max": 1},
                "a0":    {"type": "randint", "min": 0, "max": 1},
                "b2":    {"type": "fixed", "value": 1},
                "b1":    {"type": "randint", "min": 0, "max": 1},
                "b0":    {"type": "randint", "min": 0, "max": 1},
                "total": {"type": "computed", "expr": "{a3} * 8 + {a2} * 4 + {a1} * 2 + {a0} + {b2} * 4 + {b1} * 2 + {b0}"},
                # Assemble decimal integer whose digits match the binary representation of `total`.
                # total is in [9, 22] → 4 or 5 binary digits.
                "e4":    {"type": "computed", "expr": "({total} // 16) % 2"},
                "e3":    {"type": "computed", "expr": "({total} // 8) % 2"},
                "e2":    {"type": "computed", "expr": "({total} // 4) % 2"},
                "e1":    {"type": "computed", "expr": "({total} // 2) % 2"},
                "e0":    {"type": "computed", "expr": "{total} % 2"},
                "ans":   {"type": "computed", "expr": "{e4} * 10000 + {e3} * 1000 + {e2} * 100 + {e1} * 10 + {e0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Două opțiuni: (1) adunați în baza 2 direct, cu transport (1+1=10, deci scrie 0 și trece 1); (2) convertiți în baza 10, adunați, apoi convertiți rezultatul înapoi. Răspunsul se scrie ca șir de $0$-uri și $1$-uri.",
            "placeholder": "ex: 10110",
        },
    },
    {
        "name": "Produs în baza 2 → baza 2",
        "category": "mixed_base_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Produs în baza 2 → baza 2",
            "type": "fill_blank",
            "question": "Calculați, scriind rezultatul în baza 2:  $\\overline{{{a2}{a1}{a0}}}_{{(2)}} \\cdot \\overline{{{b1}{b0}}}_{{(2)}}$",
            "params": {
                "a2":    {"type": "fixed", "value": 1},
                "a1":    {"type": "randint", "min": 0, "max": 1},
                "a0":    {"type": "randint", "min": 0, "max": 1},
                "b1":    {"type": "fixed", "value": 1},
                "b0":    {"type": "randint", "min": 0, "max": 1},
                "total": {"type": "computed", "expr": "({a2} * 4 + {a1} * 2 + {a0}) * ({b1} * 2 + {b0})"},
                # total in [4, 21] → up to 5 binary digits.
                "e4":    {"type": "computed", "expr": "({total} // 16) % 2"},
                "e3":    {"type": "computed", "expr": "({total} // 8) % 2"},
                "e2":    {"type": "computed", "expr": "({total} // 4) % 2"},
                "e1":    {"type": "computed", "expr": "({total} // 2) % 2"},
                "e0":    {"type": "computed", "expr": "{total} % 2"},
                "ans":   {"type": "computed", "expr": "{e4} * 10000 + {e3} * 1000 + {e2} * 100 + {e1} * 10 + {e0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Convertiți ambele numere în baza 10, înmulțiți, apoi convertiți rezultatul în baza 2.",
            "placeholder": "ex: 10110",
        },
    },
    {
        "name": "Diferență în baza 3 → baza 3",
        "category": "mixed_base_compute",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Diferență în baza 3 → baza 3",
            "type": "fill_blank",
            "question": "Calculați, scriind rezultatul în baza 3:  $\\overline{{{a2}{a1}{a0}}}_{{(3)}} - \\overline{{{b1}{b0}}}_{{(3)}}$",
            "params": {
                # Ensure a > b. Large 3-digit base-3 vs small 2-digit base-3.
                "a2":    {"type": "randint", "min": 1, "max": 2},
                "a1":    {"type": "randint", "min": 0, "max": 2},
                "a0":    {"type": "randint", "min": 0, "max": 2},
                "b1":    {"type": "randint", "min": 1, "max": 2},
                "b0":    {"type": "randint", "min": 0, "max": 2},
                "val_a": {"type": "computed", "expr": "{a2} * 9 + {a1} * 3 + {a0}"},
                "val_b": {"type": "computed", "expr": "{b1} * 3 + {b0}"},
                # val_a in [9, 26], val_b in [3, 8] → diff always positive.
                "total": {"type": "computed", "expr": "{val_a} - {val_b}"},
                "e2":    {"type": "computed", "expr": "({total} // 9) % 3"},
                "e1":    {"type": "computed", "expr": "({total} // 3) % 3"},
                "e0":    {"type": "computed", "expr": "{total} % 3"},
                "ans":   {"type": "computed", "expr": "{e2} * 100 + {e1} * 10 + {e0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Convertiți ambele numere în baza 10, scădeți, apoi convertiți rezultatul înapoi în baza 3. Cifrele în baza 3 pot fi $0, 1, 2$.",
            "placeholder": "ex: 121",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Different bases, result in a specified (smaller) base
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Sumă baza 3 + baza 10 → baza 3",
        "category": "mixed_base_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Sumă baza 3 + baza 10 → baza 3",
            "type": "fill_blank",
            "question": "Calculați, scriind rezultatul în baza 3:  $\\overline{{{a3}{a2}{a1}{a0}}}_{{(3)}} + {b}$",
            "params": {
                # a3 a2 a1 a0 in base 3, values in [27, 80]
                "a3":    {"type": "randint", "min": 1, "max": 2},
                "a2":    {"type": "randint", "min": 0, "max": 2},
                "a1":    {"type": "randint", "min": 0, "max": 2},
                "a0":    {"type": "randint", "min": 0, "max": 2},
                "b":     {"type": "randint", "min": 50, "max": 150},
                "val_a": {"type": "computed", "expr": "{a3} * 27 + {a2} * 9 + {a1} * 3 + {a0}"},
                # total in [77, 230] → up to 5 ternary digits (3^5 = 243).
                "total": {"type": "computed", "expr": "{val_a} + {b}"},
                "e4":    {"type": "computed", "expr": "({total} // 81) % 3"},
                "e3":    {"type": "computed", "expr": "({total} // 27) % 3"},
                "e2":    {"type": "computed", "expr": "({total} // 9) % 3"},
                "e1":    {"type": "computed", "expr": "({total} // 3) % 3"},
                "e0":    {"type": "computed", "expr": "{total} % 3"},
                "ans":   {"type": "computed", "expr": "{e4} * 10000 + {e3} * 1000 + {e2} * 100 + {e1} * 10 + {e0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Convertiți $\\overline{{{a3}{a2}{a1}{a0}}}_{{(3)}}$ în baza 10, adunați cu ${b}$, apoi convertiți rezultatul în baza 3 prin împărțiri succesive la $3$.",
            "placeholder": "ex: 21012",
        },
    },
    {
        "name": "Produs baza 2 · baza 2 → baza 2 (operanzi 4 cifre)",
        "category": "mixed_base_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Produs baza 2 · baza 2 → baza 2 (operanzi 4 cifre)",
            "type": "fill_blank",
            "question": "Calculați, scriind rezultatul în baza 2:  $\\overline{{{a3}{a2}{a1}{a0}}}_{{(2)}} \\cdot \\overline{{{b1}{b0}}}_{{(2)}}$",
            "params": {
                "a3":    {"type": "fixed", "value": 1},
                "a2":    {"type": "randint", "min": 0, "max": 1},
                "a1":    {"type": "randint", "min": 0, "max": 1},
                "a0":    {"type": "randint", "min": 0, "max": 1},
                "b1":    {"type": "fixed", "value": 1},
                "b0":    {"type": "randint", "min": 0, "max": 1},
                "val_a": {"type": "computed", "expr": "{a3} * 8 + {a2} * 4 + {a1} * 2 + {a0}"},
                "val_b": {"type": "computed", "expr": "{b1} * 2 + {b0}"},
                # total in [8·2, 15·3] = [16, 45] → 5 or 6 binary digits.
                "total": {"type": "computed", "expr": "{val_a} * {val_b}"},
                "e5":    {"type": "computed", "expr": "({total} // 32) % 2"},
                "e4":    {"type": "computed", "expr": "({total} // 16) % 2"},
                "e3":    {"type": "computed", "expr": "({total} // 8) % 2"},
                "e2":    {"type": "computed", "expr": "({total} // 4) % 2"},
                "e1":    {"type": "computed", "expr": "({total} // 2) % 2"},
                "e0":    {"type": "computed", "expr": "{total} % 2"},
                "ans":   {"type": "computed", "expr": "{e5} * 100000 + {e4} * 10000 + {e3} * 1000 + {e2} * 100 + {e1} * 10 + {e0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Convertiți ambele numere în baza 10, înmulțiți, apoi convertiți rezultatul înapoi în baza 2.",
            "placeholder": "ex: 101101",
        },
    },
    {
        "name": "Cât exact baza 10 → baza 2",
        "category": "mixed_base_compute",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Cât exact baza 10 → baza 2",
            "type": "fill_blank",
            "question": "Calculați, scriind rezultatul în baza 2:  ${a} : {b}$",
            "params": {
                # Ensure exact division: a = b * q.
                "b":     {"type": "randint", "min": 3, "max": 15},
                "q":     {"type": "randint", "min": 8, "max": 50},
                "a":     {"type": "computed", "expr": "{b} * {q}"},
                # q in [8, 50] → up to 6 binary digits.
                "e5":    {"type": "computed", "expr": "({q} // 32) % 2"},
                "e4":    {"type": "computed", "expr": "({q} // 16) % 2"},
                "e3":    {"type": "computed", "expr": "({q} // 8) % 2"},
                "e2":    {"type": "computed", "expr": "({q} // 4) % 2"},
                "e1":    {"type": "computed", "expr": "({q} // 2) % 2"},
                "e0":    {"type": "computed", "expr": "{q} % 2"},
                "ans":   {"type": "computed", "expr": "{e5} * 100000 + {e4} * 10000 + {e3} * 1000 + {e2} * 100 + {e1} * 10 + {e0}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Efectuați împărțirea în baza 10, apoi convertiți câtul în baza 2 prin împărțiri succesive la $2$.",
            "placeholder": "ex: 101011",
        },
    },
]
