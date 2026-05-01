"""
Glossary terms — Grade 5, Unit 1 (Numere naturale)

Loaded by:
    python manage.py load_glossary glossary.grade5_unit1
    python manage.py load_glossary glossary.grade5_unit1 --flush

UNIT resolves the Unit FK once for every term in this file.
TERMS is a list of dicts whose keys mirror the GlossaryTerm model:
    term, aliases, definition, category, examples
"""

"""
Glossary terms for Grade 5 / Unit 1 — Numere Naturale.

PLACEHOLDER CONTENT — drafted automatically based on lesson content.
Teacher review required before treating these as finalized:
  - Definitions may need rephrasing for Grade 5 register
  - Aliases (inflected forms) may need expansion or correction
  - Examples may need to align with the teacher's preferred conventions
  - Some terms may be unnecessary; others may be missing

Categories used: definition, notation, property
"""

UNIT = {"grade": 5, "order": 1}

TERMS = [
    # ─── Batch 1: Place value & decimal writing (Lessons 1.1, 1.14) ──────────
    {
        "term": "număr natural",
        "aliases": ["numere", "numărul", "numerele", "numerelor", "numere naturale", "numerelor naturale"],
        "definition": "Un număr folosit pentru a număra obiecte sau pentru a indica o poziție într-un șir. Numerele naturale sunt $0, 1, 2, 3, 4, \\ldots$ și continuă la infinit.",
        "category": "definition",
        "examples": [
            "$5$, $42$ și $1000$ sunt numere naturale.",
            "Cel mai mic număr natural este $0$.",
        ],
    },
    {
        "term": "cifră",
        "aliases": ["cifre", "cifrele", "cifrei", "cifrelor"],
        "definition": "Unul dintre cele zece simboluri folosite pentru a scrie numerele: $0, 1, 2, 3, 4, 5, 6, 7, 8, 9$. Acestea se numesc cifre arabe.",
        "category": "definition",
        "examples": [
            "Numărul $358$ are trei cifre: $3$, $5$ și $8$.",
            "Cifra unităților lui $147$ este $7$.",
        ],
    },
    {
        "term": "ordin",
        "aliases": ["ordine", "ordinul", "ordinele", "ordinelor"],
        "definition": "Poziția ocupată de o cifră într-un număr. De la dreapta spre stânga: ordinul unităților, ordinul zecilor, ordinul sutelor, ordinul miilor și așa mai departe. Zece unități de un ordin formează o unitate de ordin imediat superior.",
        "category": "definition",
        "examples": [
            "În numărul $4582$, cifra $8$ este la ordinul zecilor.",
            "$10$ zeci formează o sută; $10$ sute formează o mie.",
        ],
    },
    {
        "term": "clasă",
        "aliases": ["clase", "clasa", "claselor", "clasele"],
        "definition": "Un grup de trei ordine consecutive, format pentru a citi numerele mari mai ușor. Clasele se numără de la dreapta spre stânga: clasa unităților, clasa miilor, clasa milioanelor, clasa miliardelor.",
        "category": "definition",
        "examples": [
            "În numărul $23\\,472\\,508\\,216$, $508$ este clasa miilor.",
            "Clasa unităților conține ordinele unităților, zecilor și sutelor.",
        ],
    },
    {
        "term": "sistem zecimal",
        "aliases": ["sistemul zecimal", "scrierea în baza zece", "baza 10", "baza zece", "sistem de numerație zecimal"],
        "definition": "Modul standard de scriere a numerelor naturale folosind cele zece cifre arabe. Se numește zecimal pentru că zece unități de un ordin formează o unitate de ordin superior.",
        "category": "definition",
        "examples": [
            "$235$ scris în sistem zecimal înseamnă $2 \\times 100 + 3 \\times 10 + 5$.",
        ],
    },
    {
        "term": "formă canonică",
        "aliases": ["forma canonică", "descompunere", "descompunerea", "descompunere zecimală"],
        "definition": "Scrierea unui număr natural ca sumă de produse între fiecare cifră și valoarea ordinului său.",
        "category": "definition",
        "examples": [
            "$137 = 1 \\times 100 + 3 \\times 10 + 7 \\times 1$",
            "$\\overline{ab} = a \\times 10 + b$ este forma canonică a unui număr de două cifre.",
        ],
    },

    # ─── Batch 2: Comparison, ordering, number line (Lesson 1.2) ─────────────
    {
        "term": "axa numerelor",
        "aliases": ["axă", "axa", "pe axa numerelor"],
        "definition": "O dreaptă pe care alegem un punct numit origine (asociat cu $0$) și o unitate de măsură. Pe axă putem reprezenta numerele naturale prin puncte echidistante, în ordine crescătoare de la stânga spre dreapta.",
        "category": "definition",
        "examples": [
            "Pe axa numerelor, $5$ este la dreapta lui $3$, deci $5 > 3$.",
        ],
    },
    {
        "term": "predecesor",
        "aliases": ["predecesorul", "predecesori"],
        "definition": "Numărul natural care vine imediat înaintea unui număr dat. Predecesorul lui $n$ este $n - 1$. Numărul $0$ nu are predecesor în mulțimea numerelor naturale.",
        "category": "definition",
        "examples": [
            "Predecesorul lui $7$ este $6$.",
            "Predecesorul lui $100$ este $99$.",
        ],
    },
    {
        "term": "succesor",
        "aliases": ["succesorul", "succesori"],
        "definition": "Numărul natural care vine imediat după un număr dat. Succesorul lui $n$ este $n + 1$. Orice număr natural are un succesor.",
        "category": "definition",
        "examples": [
            "Succesorul lui $7$ este $8$.",
            "Succesorul lui $999$ este $1000$.",
        ],
    },
    {
        "term": "ordine crescătoare",
        "aliases": ["ordonare crescătoare", "crescător", "ordonare ascendentă"],
        "definition": "Aranjarea numerelor de la cel mai mic la cel mai mare.",
        "category": "definition",
        "examples": [
            "În ordine crescătoare: $3 < 7 < 12 < 25$.",
        ],
    },
    {
        "term": "ordine descrescătoare",
        "aliases": ["ordonare descrescătoare", "descrescător", "ordonare descendentă"],
        "definition": "Aranjarea numerelor de la cel mai mare la cel mai mic.",
        "category": "definition",
        "examples": [
            "În ordine descrescătoare: $25 > 12 > 7 > 3$.",
        ],
    },
    {
        "term": "<",
        "aliases": ["mai mic", "mai mic decât", "strict mai mic"],
        "definition": "Simbolul „mai mic decât”. $a < b$ înseamnă că $a$ este strict mai mic decât $b$.",
        "category": "notation",
        "examples": [
            "$3 < 5$",
            "$0 < 1$",
        ],
    },
    {
        "term": ">",
        "aliases": ["mai mare", "mai mare decât", "strict mai mare"],
        "definition": "Simbolul „mai mare decât”. $a > b$ înseamnă că $a$ este strict mai mare decât $b$.",
        "category": "notation",
        "examples": [
            "$8 > 5$",
            "$100 > 99$",
        ],
    },
    {
        "term": "≤",
        "aliases": ["<=", "mai mic sau egal"],
        "definition": "Simbolul „mai mic sau egal”. $a \\leq b$ înseamnă că $a$ este mai mic decât $b$ sau egal cu $b$.",
        "category": "notation",
        "examples": [
            "$3 \\leq 5$ este adevărat.",
            "$7 \\leq 7$ este adevărat (egalitatea contează).",
            "$9 \\leq 4$ este fals.",
        ],
    },
    {
        "term": "≥",
        "aliases": [">=", "mai mare sau egal"],
        "definition": "Simbolul „mai mare sau egal”. $a \\geq b$ înseamnă că $a$ este mai mare decât $b$ sau egal cu $b$.",
        "category": "notation",
        "examples": [
            "$8 \\geq 5$ este adevărat.",
            "$7 \\geq 7$ este adevărat.",
            "$3 \\geq 9$ este fals.",
        ],
    },

    # ─── Batch 3: Approximation (Lesson 1.3) ─────────────────────────────────
    {
        "term": "aproximare",
        "aliases": ["aproximări", "aproximarea", "a aproxima", "aproximat"],
        "definition": "Înlocuirea unui număr cu un alt număr apropiat, mai simplu de folosit. Aproximarea poate fi prin lipsă (mai mică decât numărul original) sau prin adaos (mai mare decât numărul original).",
        "category": "definition",
        "examples": [
            "$1204$ aproximat la zeci este $1200$.",
            "Populația României de aproximativ $19$ milioane este o aproximare a numărului real.",
        ],
    },
    {
        "term": "aproximare prin lipsă",
        "aliases": ["prin lipsă", "rotunjire prin lipsă"],
        "definition": "Aproximarea unui număr cu un alt număr mai mic decât el, obținut prin înlocuirea cifrelor de la un anumit ordin în jos cu zerouri.",
        "category": "definition",
        "examples": [
            "$1247$ aproximat prin lipsă la sute este $1200$.",
            "$58$ aproximat prin lipsă la zeci este $50$.",
        ],
    },
    {
        "term": "aproximare prin adaos",
        "aliases": ["prin adaos", "rotunjire prin adaos"],
        "definition": "Aproximarea unui număr cu un alt număr mai mare decât el, obținut prin creșterea cu o unitate a cifrei de la ordinul considerat și înlocuirea cu zerouri a cifrelor inferioare.",
        "category": "definition",
        "examples": [
            "$1247$ aproximat prin adaos la sute este $1300$.",
            "$58$ aproximat prin adaos la zeci este $60$.",
        ],
    },
    {
        "term": "≈",
        "aliases": ["aproximativ egal", "aproximativ"],
        "definition": "Simbolul „aproximativ egal cu”. $a \\approx b$ înseamnă că $a$ este aproximativ egal cu $b$.",
        "category": "notation",
        "examples": [
            "$1247 \\approx 1250$",
            "$998 \\approx 1000$",
        ],
    },

    # ─── Batch 4: Addition, subtraction, properties (Lessons 1.4–1.6) ────────
    {
        "term": "adunare",
        "aliases": ["adunări", "adunarea", "a aduna", "adună"],
        "definition": "Operația matematică prin care din două sau mai multe numere se obține un singur număr, numit sumă.",
        "category": "definition",
        "examples": [
            "$3 + 5 = 8$ este o adunare.",
        ],
    },
    {
        "term": "sumă",
        "aliases": ["sume", "suma", "sumei", "sumelor"],
        "definition": "Rezultatul unei adunări. În scrierea $a + b = s$, numărul $s$ se numește suma lui $a$ și $b$.",
        "category": "definition",
        "examples": [
            "Suma numerelor $4$ și $9$ este $13$.",
            "Suma cifrelor lui $234$ este $2 + 3 + 4 = 9$.",
        ],
    },
    {
        "term": "termen",
        "aliases": ["termeni", "termenii", "termenilor"],
        "definition": "Fiecare dintre numerele care se adună într-o sumă. În scrierea $a + b = s$, numerele $a$ și $b$ se numesc termeni.",
        "category": "definition",
        "examples": [
            "În adunarea $7 + 12 = 19$, termenii sunt $7$ și $12$.",
        ],
    },
    {
        "term": "comutativitate",
        "aliases": ["comutativă", "proprietatea de comutativitate", "comutativ"],
        "definition": "Proprietatea care spune că ordinea termenilor (sau a factorilor) nu schimbă rezultatul. Adunarea și înmulțirea sunt comutative; scăderea și împărțirea nu sunt.",
        "category": "property",
        "examples": [
            "$3 + 5 = 5 + 3$",
            "$4 \\times 7 = 7 \\times 4$",
        ],
    },
    {
        "term": "asociativitate",
        "aliases": ["asociativă", "proprietatea de asociativitate", "asociativ"],
        "definition": "Proprietatea care spune că modul în care grupăm termenii (sau factorii) nu schimbă rezultatul. Adunarea și înmulțirea sunt asociative; scăderea și împărțirea nu sunt.",
        "category": "property",
        "examples": [
            "$(2 + 3) + 4 = 2 + (3 + 4)$",
            "$(5 \\times 2) \\times 3 = 5 \\times (2 \\times 3)$",
        ],
    },
    {
        "term": "element neutru",
        "aliases": ["elementul neutru"],
        "definition": "Un număr care, atunci când este adunat sau înmulțit cu orice alt număr, lasă acel număr neschimbat. Pentru adunare, elementul neutru este $0$ ($a + 0 = a$). Pentru înmulțire, elementul neutru este $1$ ($a \\times 1 = a$).",
        "category": "property",
        "examples": [
            "$25 + 0 = 25$",
            "$17 \\times 1 = 17$",
        ],
    },
    {
        "term": "suma lui Gauss",
        "aliases": ["formula lui Gauss", "suma Gauss"],
        "definition": "Formula pentru suma primelor $n$ numere naturale consecutive nenule: $1 + 2 + 3 + \\ldots + n = \\dfrac{n(n+1)}{2}$. Numită după matematicianul Carl Friedrich Gauss.",
        "category": "property",
        "examples": [
            "$1 + 2 + 3 + \\ldots + 100 = \\dfrac{100 \\times 101}{2} = 5050$",
        ],
    },
    {
        "term": "scădere",
        "aliases": ["scăderi", "scăderea", "a scădea", "scade"],
        "definition": "Operația matematică inversă adunării. Din numărul descăzut se ia (scade) numărul scăzător pentru a obține diferența.",
        "category": "definition",
        "examples": [
            "$15 - 6 = 9$ este o scădere.",
        ],
    },
    {
        "term": "diferență",
        "aliases": ["diferențe", "diferența", "diferenței"],
        "definition": "Rezultatul unei scăderi. În scrierea $a - b = d$, numărul $d$ se numește diferența dintre $a$ și $b$.",
        "category": "definition",
        "examples": [
            "Diferența dintre $20$ și $13$ este $7$.",
        ],
    },
    {
        "term": "descăzut",
        "aliases": ["descăzutul"],
        "definition": "Numărul din care se scade într-o scădere. În scrierea $a - b = d$, numărul $a$ se numește descăzut.",
        "category": "definition",
        "examples": [
            "În scăderea $20 - 8 = 12$, descăzutul este $20$.",
        ],
    },
    {
        "term": "scăzător",
        "aliases": ["scăzătorul"],
        "definition": "Numărul care se scade într-o scădere. În scrierea $a - b = d$, numărul $b$ se numește scăzător.",
        "category": "definition",
        "examples": [
            "În scăderea $20 - 8 = 12$, scăzătorul este $8$.",
        ],
    },

    # ─── Batch 5: Multiplication & division (Lessons 1.7–1.10) ───────────────
    {
        "term": "înmulțire",
        "aliases": ["înmulțiri", "înmulțirea", "a înmulți", "înmulțește"],
        "definition": "Operația matematică prin care un număr se adună cu el însuși de un anumit număr de ori. Pe scurt, $a \\times b$ înseamnă $a$ adunat cu el însuși de $b$ ori.",
        "category": "definition",
        "examples": [
            "$4 \\times 3 = 4 + 4 + 4 = 12$",
        ],
    },
    {
        "term": "produs",
        "aliases": ["produse", "produsul", "produsului"],
        "definition": "Rezultatul unei înmulțiri. În scrierea $a \\times b = p$, numărul $p$ se numește produsul lui $a$ și $b$.",
        "category": "definition",
        "examples": [
            "Produsul numerelor $6$ și $7$ este $42$.",
        ],
    },
    {
        "term": "factor",
        "aliases": ["factori", "factorii", "factorilor"],
        "definition": "Fiecare dintre numerele care se înmulțesc într-un produs. În scrierea $a \\times b = p$, numerele $a$ și $b$ se numesc factori.",
        "category": "definition",
        "examples": [
            "În înmulțirea $5 \\times 8 = 40$, factorii sunt $5$ și $8$.",
        ],
    },
    {
        "term": "distributivitate",
        "aliases": ["distributivă", "proprietatea de distributivitate", "distributiv"],
        "definition": "Proprietatea care permite distribuirea unui factor peste o sumă sau diferență: $a \\times (b + c) = a \\times b + a \\times c$. Înmulțirea este distributivă față de adunare și scădere.",
        "category": "property",
        "examples": [
            "$5 \\times (3 + 4) = 5 \\times 3 + 5 \\times 4 = 15 + 20 = 35$",
        ],
    },
    {
        "term": "factor comun",
        "aliases": ["factorul comun", "scoaterea factorului comun"],
        "definition": "Un număr care apare ca factor în mai mulți termeni ai unei sume sau diferențe. Scoaterea factorului comun aplică distributivitatea în sens invers: $a \\times b + a \\times c = a \\times (b + c)$.",
        "category": "definition",
        "examples": [
            "$3 \\times 7 + 3 \\times 4 = 3 \\times (7 + 4) = 3 \\times 11 = 33$",
        ],
    },
    {
        "term": "împărțire",
        "aliases": ["împărțiri", "împărțirea", "a împărți"],
        "definition": "Operația matematică inversă înmulțirii. Prin împărțirea numărului $a$ la $b$ aflăm de câte ori se cuprinde $b$ în $a$.",
        "category": "definition",
        "examples": [
            "$20 : 4 = 5$, pentru că $4 \\times 5 = 20$.",
        ],
    },
    {
        "term": "deîmpărțit",
        "aliases": ["deîmpărțitul"],
        "definition": "Numărul care se împarte într-o împărțire. În scrierea $a : b = c$, numărul $a$ se numește deîmpărțit.",
        "category": "definition",
        "examples": [
            "În împărțirea $24 : 6 = 4$, deîmpărțitul este $24$.",
        ],
    },
    {
        "term": "împărțitor",
        "aliases": ["împărțitorul"],
        "definition": "Numărul la care se împarte într-o împărțire. În scrierea $a : b = c$, numărul $b$ se numește împărțitor. Împărțitorul nu poate fi zero.",
        "category": "definition",
        "examples": [
            "În împărțirea $24 : 6 = 4$, împărțitorul este $6$.",
        ],
    },
    {
        "term": "cât",
        "aliases": ["câtul", "câtului"],
        "definition": "Rezultatul unei împărțiri. În scrierea $a : b = c$, numărul $c$ se numește câtul împărțirii lui $a$ la $b$.",
        "category": "definition",
        "examples": [
            "Câtul împărțirii lui $30$ la $5$ este $6$.",
        ],
    },
    {
        "term": "rest",
        "aliases": ["restul", "restului"],
        "definition": "Ceea ce rămâne dintr-o împărțire care nu se face exact. La împărțirea cu rest, restul este întotdeauna mai mic decât împărțitorul.",
        "category": "definition",
        "examples": [
            "$17 : 5 = 3$ rest $2$, pentru că $5 \\times 3 + 2 = 17$.",
        ],
    },
    {
        "term": "teorema împărțirii cu rest",
        "aliases": ["teorema împărțirii", "formula împărțirii cu rest"],
        "definition": "Pentru orice numere naturale $a$ și $b$ cu $b \\neq 0$, există în mod unic numerele naturale $q$ (câtul) și $r$ (restul) astfel încât $a = b \\times q + r$, unde $0 \\leq r < b$.",
        "category": "property",
        "examples": [
            "Pentru $23 : 4$: $23 = 4 \\times 5 + 3$, deci câtul este $5$ și restul este $3$.",
        ],
    },

    # ─── Batch 6: Powers, bases, order of operations (Lessons 1.11–1.15) ─────
    {
        "term": "putere",
        "aliases": ["puteri", "puterea", "puterii", "puterilor"],
        "definition": "Înmulțirea repetată a aceluiași număr cu el însuși. Notația $a^n$ înseamnă numărul $a$ înmulțit cu el însuși de $n$ ori. $a^n$ se citește „$a$ la puterea $n$”.",
        "category": "definition",
        "examples": [
            "$2^3 = 2 \\times 2 \\times 2 = 8$",
            "$5^4 = 5 \\times 5 \\times 5 \\times 5 = 625$",
        ],
    },
    {
        "term": "bază",
        "aliases": ["baza", "bazei"],
        "definition": "În scrierea unei puteri $a^n$, numărul $a$ se numește bază. (Termenul „bază” are și un alt sens când vorbim despre baze de numerație, ca baza 10 sau baza 2.)",
        "category": "definition",
        "examples": [
            "În $7^3$, baza este $7$.",
            "În $10^5$, baza este $10$.",
        ],
    },
    {
        "term": "exponent",
        "aliases": ["exponentul", "exponenți", "exponenții"],
        "definition": "În scrierea unei puteri $a^n$, numărul $n$ se numește exponent. El arată de câte ori se înmulțește baza cu ea însăși.",
        "category": "definition",
        "examples": [
            "În $7^3$, exponentul este $3$.",
            "$a^1 = a$ și, prin convenție, $a^0 = 1$ pentru orice $a \\neq 0$.",
        ],
    },
    {
        "term": "pătrat perfect",
        "aliases": ["pătrate perfecte", "pătratul perfect"],
        "definition": "Un număr natural care poate fi scris ca pătratul unui alt număr natural, adică $n^2$ pentru un $n$ natural. Primele pătrate perfecte sunt $0, 1, 4, 9, 16, 25, 36, \\ldots$",
        "category": "definition",
        "examples": [
            "$49$ este pătrat perfect, pentru că $49 = 7^2$.",
            "$50$ nu este pătrat perfect.",
        ],
    },
    {
        "term": "cub perfect",
        "aliases": ["cuburi perfecte", "cubul perfect"],
        "definition": "Un număr natural care poate fi scris ca cubul unui alt număr natural, adică $n^3$ pentru un $n$ natural. Primele cuburi perfecte sunt $0, 1, 8, 27, 64, 125, \\ldots$",
        "category": "definition",
        "examples": [
            "$125$ este cub perfect, pentru că $125 = 5^3$.",
            "$100$ nu este cub perfect.",
        ],
    },
    {
        "term": "sistem binar",
        "aliases": ["sistemul binar", "baza 2", "scrierea în baza 2", "sistem de numerație binar"],
        "definition": "Sistemul de numerație care folosește doar două cifre: $0$ și $1$. Două unități de un anumit ordin formează o unitate de ordin imediat superior. Este sistemul folosit de computere.",
        "category": "definition",
        "examples": [
            "$111_{(2)} = 1 \\times 2^2 + 1 \\times 2^1 + 1 \\times 2^0 = 7$",
            "$10_{(2)} = 2$ în baza $10$.",
        ],
    },
    {
        "term": "ordinea operațiilor",
        "aliases": ["ordinea efectuării operațiilor", "ordinea operatiilor"],
        "definition": "Regula care stabilește în ce ordine se efectuează operațiile într-un calcul: 1) parantezele, începând cu cele mai interioare; 2) puterile; 3) înmulțirile și împărțirile, de la stânga la dreapta; 4) adunările și scăderile, de la stânga la dreapta.",
        "category": "property",
        "examples": [
            "$3 + 4 \\times 2 = 3 + 8 = 11$ (înmulțirea înainte de adunare).",
            "$(3 + 4) \\times 2 = 7 \\times 2 = 14$ (parantezele schimbă ordinea).",
        ],
    },
]