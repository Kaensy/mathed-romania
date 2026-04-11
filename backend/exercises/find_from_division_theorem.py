"""
Exercise data: find_from_division_theorem
Topic 1.7 — Împărțirea (lesson 7.2: Împărțirea cu rest)

Category: find_from_division_theorem
Label (RO): Teorema împărțirii cu rest

Tiers:
  Easy   — Direct application: given b, q, r → find a; given a, r → find b, q
  Medium — Sum/difference + division reverse problems
  Hard   — Multi-constraint: consecutive sums, special remainder properties

All templates guarantee natural-number solutions with r < b constraint.

Usage:
    python manage.py load_exercises exercises.find_from_division_theorem
    python manage.py load_exercises exercises.find_from_division_theorem --flush
"""

TOPIC = {
    "grade": 5,
    "unit_order": 1,
    "topic_order": 7,  # "Împărțirea"
}

EXERCISES = [

    # ══════════════════════════════════════════════════════════════════════════
    # EASY — Direct application of a = b·q + r
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Aflați deîmpărțitul: b, q, r date",
        "category": "find_from_division_theorem",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Aflați deîmpărțitul: b, q, r date",
            "type": "fill_blank",
            "question": "Determinați numărul natural care împărțit la ${b}$ dă câtul ${q}$ și restul ${r}$.",
            "params": {
                "b": {"type": "randint", "min": 5, "max": 30},
                "q": {"type": "randint", "min": 3, "max": 50},
                "r": {"type": "randint", "min": 1, "max": "{b} - 1"},
                "a": {"type": "computed", "expr": "{b} * {q} + {r}"},
            },
            "answer_expr": "{a}",
            "answer_input": "number",
            "hint": "Folosiți teorema împărțirii cu rest: $a = b \\cdot q + r = {b} \\cdot {q} + {r}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Aflați împărțitorul: a, q, r date",
        "category": "find_from_division_theorem",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Aflați împărțitorul: a, q, r date",
            "type": "fill_blank",
            "question": "Determinați împărțitorul, știind că deîmpărțitul este ${a}$, câtul este ${q}$ și restul este ${r}$.",
            "params": {
                "b": {"type": "randint", "min": 5, "max": 30},
                "q": {"type": "randint", "min": 3, "max": 50},
                "r": {"type": "randint", "min": 1, "max": "{b} - 1"},
                "a": {"type": "computed", "expr": "{b} * {q} + {r}"},
            },
            "answer_expr": "{b}",
            "answer_input": "number",
            "hint": "Din $a = b \\cdot q + r$ rezultă $b = (a - r) : q = ({a} - {r}) : {q}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Aflați câtul: a, b, r date",
        "category": "find_from_division_theorem",
        "difficulty": "easy",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Aflați câtul: a, b, r date",
            "type": "fill_blank",
            "question": "Determinați câtul, știind că deîmpărțitul este ${a}$, împărțitorul este ${b}$ și restul este ${r}$.",
            "params": {
                "b": {"type": "randint", "min": 5, "max": 30},
                "q": {"type": "randint", "min": 3, "max": 50},
                "r": {"type": "randint", "min": 1, "max": "{b} - 1"},
                "a": {"type": "computed", "expr": "{b} * {q} + {r}"},
            },
            "answer_expr": "{q}",
            "answer_input": "number",
            "hint": "Din $a = b \\cdot q + r$ rezultă $q = (a - r) : b = ({a} - {r}) : {b}$.",
            "placeholder": "= ?",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MEDIUM — Sum/difference + division reverse
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Sumă și împărțire: suma S, q și r date",
        "category": "find_from_division_theorem",
        "difficulty": "medium",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Sumă și împărțire",
            "type": "multi_fill_blank",
            "question": "Suma a două numere naturale este ${s}$. Știind că împărțind numărul mai mare la numărul mai mic obținem câtul ${q}$ și restul ${r}$, determinați cele două numere.",
            "params": {
                "small": {"type": "randint", "min": 5, "max": 30},
                "q":     {"type": "randint", "min": 2, "max": 6},
                "r":     {"type": "randint", "min": 1, "max": "{small} - 1"},
                "big":   {"type": "computed", "expr": "{small} * {q} + {r}"},
                "s":     {"type": "computed", "expr": "{small} + {big}"},
            },
            "fields": [
                {"key": "big",   "label": "Numărul mai mare", "answer_expr": "{big}"},
                {"key": "small", "label": "Numărul mai mic",  "answer_expr": "{small}"},
            ],
            "answer_input": "number",
            "hint": "Dacă numărul mic este $n$, atunci cel mare este $n \\cdot {q} + {r}$. Suma lor este $n + n \\cdot {q} + {r} = {s}$, deci $n \\cdot ({q}+1) = {s} - {r}$.",
        },
    },
    {
        "name": "Diferență și împărțire: diferența D, q și r date",
        "category": "find_from_division_theorem",
        "difficulty": "medium",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Diferență și împărțire",
            "type": "multi_fill_blank",
            "question": "Diferența a două numere naturale este ${d}$. Știind că împărțind numărul mai mare la numărul mai mic obținem câtul ${q}$ și restul ${r}$, determinați cele două numere.",
            "params": {
                "small": {"type": "randint", "min": 5, "max": 30},
                "q":     {"type": "randint", "min": 3, "max": 10},
                "r":     {"type": "randint", "min": 1, "max": "{small} - 1"},
                "big":   {"type": "computed", "expr": "{small} * {q} + {r}"},
                "d":     {"type": "computed", "expr": "{big} - {small}"},
            },
            "fields": [
                {"key": "big",   "label": "Numărul mai mare", "answer_expr": "{big}"},
                {"key": "small", "label": "Numărul mai mic",  "answer_expr": "{small}"},
            ],
            "answer_input": "number",
            "hint": "Dacă numărul mic este $n$, atunci cel mare este $n \\cdot {q} + {r}$. Diferența este $n \\cdot {q} + {r} - n = n \\cdot ({q}-1) + {r} = {d}$.",
        },
    },
    {
        "name": "Număr de k ori mai mare, în interval",
        "category": "find_from_division_theorem",
        "difficulty": "medium",
        "exercise_type": "multi_fill_blank",
        "template": {
            "title": "Număr de k ori mai mare, în interval",
            "type": "multi_fill_blank",
            "question": "Un număr natural este de ${k}$ ori mai mare decât alt număr natural. Care sunt cele două numere, știind că cel mare este mai mare decât ${lo}$ și mai mic decât ${hi}$?",
            "params": {
                "k":     {"type": "randint", "min": 5, "max": 13},
                "small": {"type": "randint", "min": 7, "max": 20},
                "big":   {"type": "computed", "expr": "{k} * {small}"},
                "lo":    {"type": "computed", "expr": "{big} - {k}"},
                "hi":    {"type": "computed", "expr": "{big} + {k}"},
            },
            "fields": [
                {"key": "big",   "label": "Numărul mai mare", "answer_expr": "{big}"},
                {"key": "small", "label": "Numărul mai mic",  "answer_expr": "{small}"},
            ],
            "answer_input": "number",
            "hint": "Numărul mare se împarte exact la ${k}$. Căutați singurul multiplu al lui ${k}$ în intervalul $({lo}, {hi})$.",
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HARD — Multi-constraint problems
    # ══════════════════════════════════════════════════════════════════════════

    {
        "name": "Cel mai mare număr de n cifre cu rest dat",
        "category": "find_from_division_theorem",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Cel mai mare număr de n cifre cu rest dat",
            "type": "fill_blank",
            "question": "Care este cel mai mare număr de ${digits}$ cifre care împărțit la ${b}$ dă restul ${r}$?",
            "params": {
                "digits":  {"type": "choice", "options": [3, 4]},
                "b":       {"type": "randint", "min": 7, "max": 30},
                "r":       {"type": "randint", "min": 1, "max": "{b} - 1"},
                "upper":   {"type": "computed", "expr": "10 ** {digits} - 1"},
                "q_max":   {"type": "computed", "expr": "({upper} - {r}) // {b}"},
                "ans":     {"type": "computed", "expr": "{b} * (({upper} - {r}) // {b}) + {r}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Cel mai mare număr de ${digits}$ cifre este ${upper}$. Împărțim $({upper} - {r})$ la ${b}$ pentru a afla câtul maxim ${q_max}$, apoi calculăm ${b} \\cdot {q_max} + {r}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Cel mai mic număr de n cifre cu rest dat",
        "category": "find_from_division_theorem",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Cel mai mic număr de n cifre cu rest dat",
            "type": "fill_blank",
            "question": "Care este cel mai mic număr de ${digits}$ cifre care împărțit la ${b}$ dă restul ${r}$?",
            "params": {
                "digits": {"type": "choice", "options": [3, 4]},
                "b":      {"type": "randint", "min": 7, "max": 30},
                "r":      {"type": "randint", "min": 1, "max": "{b} - 1"},
                "lower":  {"type": "computed", "expr": "10 ** ({digits} - 1)"},
                "diff":   {"type": "computed", "expr": "({lower} - {r} + {b} - 1) // {b}"},
                "ans":    {"type": "computed", "expr": "{b} * (({lower} - {r} + {b} - 1) // {b}) + {r}"},
            },
            "answer_expr": "{ans}",
            "answer_input": "number",
            "hint": "Cel mai mic număr de ${digits}$ cifre este ${lower}$. Găsim cel mai mic cât $q$ astfel încât ${b} \\cdot q + {r} \\geq {lower}$.",
            "placeholder": "= ?",
        },
    },
    {
        "name": "Suma consecutivă împărțită la k",
        "category": "find_from_division_theorem",
        "difficulty": "hard",
        "exercise_type": "fill_blank",
        "template": {
            "title": "Suma consecutivă împărțită la k",
            "type": "fill_blank",
            "question": "Suma a cinci numere naturale consecutive se împarte la ${k}$ și se obține câtul ${q}$ și restul ${r}$. Determinați cel mai mic dintre cele cinci numere.",
            "params": {
                "k":     {"type": "randint", "min": 15, "max": 30},
                "first": {"type": "randint", "min": 20, "max": 200},
                "mid":   {"type": "computed", "expr": "{first} + 2"},
                "total": {"type": "computed", "expr": "5 * ({first} + 2)"},
                "q":     {"type": "computed", "expr": "{total} // {k}"},
                "r":     {"type": "computed", "expr": "{total} % {k}"},
            },
            "answer_expr": "{first}",
            "answer_input": "number",
            "hint": "Suma = ${k} \\cdot {q} + {r} = {total}$. Suma a 5 numere consecutive este $5 \\cdot$(numărul din mijloc), deci mijlocul este ${total} : 5 = {mid}$. Cel mai mic este cu 2 mai puțin.",
            "placeholder": "= ?",
        },
    },
]
