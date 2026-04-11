"""
Exercise data: find_x_multiplication
Topic 1.6 — Înmulțirea numerelor naturale

Category: find_x_multiplication
Label (RO): Aflarea necunoscutei (înmulțire)

Tiers:
  Easy   — Direct equations: a·x=b, x·a=b, product of two with one known
  Medium — Word problems (real-world scenarios), products with conditions
  Hard   — Optimization (max/min product/sum), range problems, multi-constraint

Usage:
    python manage.py load_exercises exercises.find_x_multiplication
    python manage.py load_exercises exercises.find_x_multiplication --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 6,  # "Înmulțirea numerelor naturale"
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Direct equations
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Necunoscută: a · x = b",
        "category": "find_x_multiplication",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: a · x = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  ${a} \\cdot x = {b}$",
            "params": {
                "x": {"type": "randint", "min": 2, "max": 100},
                "a": {"type": "randint", "min": 2, "max": 50},
                "b": {"type": "computed", "expr": "{a} * {x}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Dacă ${a} \\cdot x = {b}$, atunci $x = {b} : {a}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Necunoscută: x · a = b",
        "category": "find_x_multiplication",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Necunoscută: x · a = b",
            "type": "fill_blank",
            "question": "Găsiți numărul natural $x$ care verifică egalitatea:  $x \\cdot {a} = {b}$",
            "params": {
                "x": {"type": "randint", "min": 2, "max": 100},
                "a": {"type": "randint", "min": 2, "max": 50},
                "b": {"type": "computed", "expr": "{x} * {a}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Dacă $x \\cdot {a} = {b}$, atunci $x = {b} : {a}$.",
            "placeholder": "x = ?",
        },
    },
    {
        "name": "Produsul a două numere: aflați celălalt factor",
        "category": "find_x_multiplication",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Produsul a două numere: aflați celălalt factor",
            "type": "fill_blank",
            "question": "Produsul a două numere naturale este ${p}$. Unul dintre ele este ${a}$. Determinați celălalt număr.",
            "params": {
                "x": {"type": "randint", "min": 3, "max": 100},
                "a": {"type": "randint", "min": 2, "max": 50},
                "p": {"type": "computed", "expr": "{a} * {x}"},
            },
            "answer_expr": "{x}",
            "answer_input": "number",
            "hint": "Dacă ${a} \\cdot x = {p}$, atunci $x = {p} : {a}$.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Word problems
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Problemă: livadă cu rânduri de pomi",
        "category": "find_x_multiplication",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Problemă: livadă cu rânduri de pomi",
            "type": "fill_blank",
            "question": "Într-o livadă sunt ${rows}$ rânduri, iar pe fiecare rând sunt plantați ${per_row}$ cireși. Determinați numărul total de cireși din livadă.",
            "params": {
                "rows":    {"type": "randint", "min": 15, "max": 60},
                "per_row": {"type": "randint", "min": 10, "max": 30},
            },
            "answer_expr": "{rows} * {per_row}",
            "answer_input": "number",
            "hint": "Înmulțiți numărul de rânduri cu numărul de cireși de pe fiecare rând.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Problemă: cutii cu pastile în lăzi",
        "category": "find_x_multiplication",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Problemă: cutii cu pastile în lăzi",
            "type": "fill_blank",
            "question": "Într-o cutie de medicamente sunt ${foils}$ folii cu pilule. Fiecare folie conține ${pills}$ pilule. Cutiile sunt ambalate câte ${per_crate}$ într-o ladă. Determinați numărul pilulelor existente în ${crates}$ lăzi.",
            "params": {
                "foils":     {"type": "randint", "min": 5, "max": 12},
                "pills":     {"type": "randint", "min": 8, "max": 20},
                "per_crate": {"type": "randint", "min": 6, "max": 15},
                "crates":    {"type": "randint", "min": 10, "max": 25},
            },
            "answer_expr": "{foils} * {pills} * {per_crate} * {crates}",
            "answer_input": "number",
            "hint": "Calculați pas cu pas: pilule într-o cutie = ${foils} \\cdot {pills}$, apoi pilule într-o ladă, apoi pilule în ${crates}$ lăzi.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Problemă: cutii cu urne și bile",
        "category": "find_x_multiplication",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Problemă: cutii cu urne și bile",
            "type": "fill_blank",
            "question": "Vlad are ${boxes}$ cutii. În fiecare cutie sunt ${urns}$ urne. Fiecare urnă conține ${balls}$ bile. Determinați numărul total de bile.",
            "params": {
                "boxes": {"type": "randint", "min": 3, "max": 8},
                "urns":  {"type": "randint", "min": 10, "max": 20},
                "balls": {"type": "randint", "min": 15, "max": 30},
            },
            "answer_expr": "{boxes} * {urns} * {balls}",
            "answer_input": "number",
            "hint": "Înmulțiți cele trei numere: ${boxes} \\cdot {urns} \\cdot {balls}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Problemă: bibliotecă cu rafturi mixte",
        "category": "find_x_multiplication",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Problemă: bibliotecă cu rafturi mixte",
            "type": "fill_blank",
            "question": "Într-o bibliotecă sunt rafturi cu cărți. Primele ${s1}$ rafturi conțin câte ${b1}$ cărți de matematică, iar ultimele ${s2}$ rafturi câte ${b2}$ cărți de literatură. Câte cărți sunt în bibliotecă?",
            "params": {
                "s1": {"type": "randint", "min": 3, "max": 8},
                "b1": {"type": "randint", "min": 10, "max": 20},
                "s2": {"type": "randint", "min": 2, "max": 6},
                "b2": {"type": "randint", "min": 10, "max": 20},
            },
            "answer_expr": "{s1} * {b1} + {s2} * {b2}",
            "answer_input": "number",
            "hint": "Calculați separat cărțile de matematică (${s1} \\cdot {b1}$) și pe cele de literatură (${s2} \\cdot {b2}$), apoi adunați.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Problemă: produsul a 3 numere cu condiție",
        "category": "find_x_multiplication",
        "difficulty": "medium",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Problemă: produsul a 3 numere cu condiție",
            "type": "fill_blank",
            "question": "Produsul a trei numere naturale este ${p}$. Primul număr este ${a}$, iar al doilea număr este cu ${diff}$ mai mare decât primul. Determinați al treilea număr.",
            "params": {
                "a":    {"type": "randint", "min": 3, "max": 15},
                "diff": {"type": "randint", "min": 2, "max": 10},
                "c":    {"type": "randint", "min": 2, "max": 30},
                "b":    {"type": "computed", "expr": "{a} + {diff}"},
                "p":    {"type": "computed", "expr": "{a} * {b} * {c}"},
            },
            "answer_expr": "{c}",
            "answer_input": "number",
            "hint": "Al doilea număr este ${a} + {diff} = {b}$. Apoi $x = {p} : ({a} \\cdot {b})$.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Optimization, ranges, multi-constraint
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Produs maxim: două numere cu sumă dată",
        "category": "find_x_multiplication",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Produs maxim: două numere cu sumă dată",
            "type": "fill_blank",
            "question": "Care este cea mai mare valoare posibilă a produsului a două numere naturale cu suma ${s}$?",
            "params": {
                "s":   {"type": "randint", "min": 6, "max": 30},
                "half": {"type": "computed", "expr": "{s} // 2"},
                "other": {"type": "computed", "expr": "{s} - {s} // 2"},
                "ans": {"type": "computed", "expr": "({s} // 2) * ({s} - {s} // 2)"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Produsul este maxim când cele două numere sunt cât mai apropiate. Pentru suma ${s}$, alegeți ${half}$ și ${other}$.",
            "placeholder": "Produs maxim = ?",
        },
    },
    {
        "name": "Sumă maximă: două numere cu produs dat",
        "category": "find_x_multiplication",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Sumă maximă: două numere cu produs dat",
            "type": "fill_blank",
            "question": "Care este cea mai mare valoare posibilă a sumei a două numere naturale cu produsul ${p}$?",
            "params": {
                "p":   {"type": "choice", "options": [12, 18, 24, 30, 36, 48, 60]},
                "ans": {"type": "computed", "expr": "1 + {p}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Suma este maximă când unul dintre numere este cât mai mic posibil. Alegeți $1$ și ${p}$: suma este $1 + {p}$.",
            "placeholder": "Sumă maximă = ?",
        },
    },
    {
        "name": "Interval produs: factori în intervale date",
        "category": "find_x_multiplication",
        "difficulty": "hard",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Interval produs: factori în intervale date",
            "type": "multi_fill_blank",
            "question": "Un factor al unei înmulțiri este cuprins între ${a1}$ și ${a2}$, iar celălalt între ${b1}$ și ${b2}$. Între ce numere este cuprins produsul lor?",
            "params": {
                "a1":  {"type": "randint", "min": 5, "max": 30},
                "a2":  {"type": "randint", "min": 40, "max": 80},
                "b1":  {"type": "randint", "min": 10, "max": 50},
                "b2":  {"type": "randint", "min": 100, "max": 300},
                "min_p": {"type": "computed", "expr": "{a1} * {b1}"},
                "max_p": {"type": "computed", "expr": "{a2} * {b2}"},
            },
            "fields": [
                {"key": "min", "label": "Valoarea minimă", "answer_expr": "{min_p}"},
                {"key": "max", "label": "Valoarea maximă", "answer_expr": "{max_p}"},
            ],
            "answer_input": "number",
            "hint": "Produsul minim se obține din cei mai mici factori: ${a1} \\cdot {b1}$. Produsul maxim din cei mai mari: ${a2} \\cdot {b2}$.",
        },
    },
    {
        "name": "Motociclist: traseu în 4 zile",
        "category": "find_x_multiplication",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Motociclist: traseu în 4 zile",
            "type": "fill_blank",
            "question": "Un motociclist parcurge un traseu în 4 zile astfel: în prima zi ${d1}$ km, a doua zi de ${k2}$ ori mai mulți km decât în prima zi, în a treia zi se întoarce ${d3}$ km, iar în ultima zi parcurge de ${k4}$ ori mai mulți km decât a parcurs a treia zi. Determinați lungimea traseului.",
            "params": {
                "d1": {"type": "randint", "min": 10, "max": 30},
                "k2": {"type": "randint", "min": 3, "max": 6},
                "d3": {"type": "randint", "min": 8, "max": 20},
                "k4": {"type": "randint", "min": 2, "max": 5},
            },
            "answer_expr": "{d1} + {k2} * {d1} - {d3} + {k4} * {d3}",
            "answer_input": "number",
            "hint": "Ziua 1: ${d1}$. Ziua 2: ${k2} \\cdot {d1}$. Ziua 3: $-{d3}$ (se întoarce). Ziua 4: ${k4} \\cdot {d3}$. Adunați.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Produs și sumă cu ultima cifră dată",
        "category": "find_x_multiplication",
        "difficulty": "hard",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Produs și sumă cu ultima cifră dată",
            "type": "multi_fill_blank",
            "question": "Produsul a două numere naturale este ${p}$. Știind că ultima cifră a sumei celor două numere este ${last}$, determinați cele două numere.",
            "params": {
                "a":    {"type": "choice", "options": [5, 6, 8, 10, 12, 15]},
                "b":    {"type": "choice", "options": [8, 10, 12, 15, 20]},
                "p":    {"type": "computed", "expr": "{a} * {b}"},
                "last": {"type": "computed", "expr": "({a} + {b}) % 10"},
            },
            "fields": [
                {"key": "num1", "label": "Primul număr", "answer_expr": "{a}"},
                {"key": "num2", "label": "Al doilea număr", "answer_expr": "{b}"},
            ],
            "answer_input": "number",
            "hint": "Căutați perechi de factori ai lui ${p}$ și verificați care pereche are suma cu ultima cifră ${last}$.",
        },
    },
]
