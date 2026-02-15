"""
Seeds the Grade 5 curriculum structure based on the project reference document.

Creates: 1 Grade, 8 Units, ~33 Lessons (with placeholder content), 8 Tests.
Lessons are created with titles and empty content — actual lesson content
is written via the Django admin CMS.

Usage:
    python manage.py seed_grade5
    python manage.py seed_grade5 --flush  # Deletes existing Grade 5 data first
"""
from django.core.management.base import BaseCommand

from apps.content.models import Grade, Lesson, Test, Unit


# Full Grade 5 curriculum from the reference document
GRADE_5_CURRICULUM = [
    {
        "order": 1,
        "title": "Numere Naturale",
        "description": "Natural Numbers — operations, properties, powers, number bases, order of operations.",
        "lessons": [
            ("Scrierea și citirea numerelor naturale", "Writing and reading natural numbers"),
            ("Reprezentarea pe axa numerelor; compararea și ordonarea", "Number line representation; comparing and ordering"),
            ("Aproximări și probleme de estimare", "Approximations and estimation problems"),
            ("Adunarea numerelor naturale; proprietăți", "Addition of natural numbers; properties"),
            ("Scăderea numerelor naturale", "Subtraction of natural numbers"),
            ("Înmulțirea numerelor naturale; proprietăți; factor comun", "Multiplication; properties; common factor"),
            ("Împărțirea cu rest 0 și cu rest a numerelor naturale; teorema împărțirii", "Division with and without remainder; division theorem"),
            ("Ridicarea la putere cu exponent natural; reguli de calcul cu puteri; pătratul și cubul", "Powers with natural exponent; calculation rules; squares and cubes"),
            ("Baze de numerație: scrierea în baza 10 și baza 2", "Number bases: writing in base 10 and base 2"),
            ("Ordinea efectuării operațiilor", "Order of operations"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 45, "exercise_count": 15},
    },
    {
        "order": 2,
        "title": "Metode Aritmetice de Rezolvare a Problemelor",
        "description": "Arithmetic Problem-Solving Methods — five classical methods for solving word problems.",
        "lessons": [
            ("Metoda reducerii la unitate", "Reduction to unity method"),
            ("Metoda comparației", "Comparison method"),
            ("Metoda figurativă", "Figurative/diagram method"),
            ("Metoda mersului invers", "Reverse/working backwards method"),
            ("Metoda falsei ipoteze", "False hypothesis method"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 40, "exercise_count": 10},
    },
    {
        "order": 3,
        "title": "Divizibilitatea Numerelor Naturale",
        "description": "Divisibility of Natural Numbers — divisors, multiples, divisibility criteria, primes.",
        "lessons": [
            ("Noțiunea de divizor și multiplu", "Concept of divisor and multiple"),
            ("Divizori comuni; multipli comuni", "Common divisors; common multiples"),
            ("Criteriile de divizibilitate cu 2, 5 și 10", "Divisibility criteria for 2, 5, and 10"),
            ("Criteriile de divizibilitate cu 3 și 9", "Divisibility criteria for 3 and 9"),
            ("Numere prime și numere compuse", "Prime and composite numbers"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 40, "exercise_count": 10},
    },
    {
        "order": 4,
        "title": "Fracții Ordinare",
        "description": "Ordinary Fractions — concepts, representation, operations, powers, percentages.",
        "lessons": [
            ("Fracții ordinare: fracții echiunitare, subunitare, supraunitare; comparare", "Ordinary fractions: unit, proper, improper; comparison"),
            ("Reprezentarea pe axa numerelor; introducerea și scoaterea întregilor", "Number line; introducing and extracting whole parts"),
            ("Amplificarea fracțiilor", "Amplifying fractions"),
            ("Simplificarea fracțiilor; CMMDC", "Simplifying fractions; GCD"),
            ("Aducerea la numitor comun; CMMMC", "Common denominator; LCM"),
            ("Adunarea și scăderea fracțiilor ordinare", "Addition and subtraction of ordinary fractions"),
            ("Înmulțirea și împărțirea fracțiilor ordinare", "Multiplication and division of ordinary fractions"),
            ("Puterea cu exponent natural a unei fracții; fracții/procente dintr-un număr", "Powers of fractions; fractions/percentages of a number"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 50, "exercise_count": 15},
    },
    {
        "order": 5,
        "title": "Fracții Zecimale",
        "description": "Decimal Fractions — operations, conversions, arithmetic mean, rational numbers.",
        "lessons": [
            ("Fracții zecimale: concept, comparare, ordonare, reprezentare pe axă", "Decimal fractions: concept, comparison, ordering, number line"),
            ("Aproximări la ordinul zecimilor/sutimilor", "Approximations to tenths/hundredths"),
            ("Adunarea și scăderea fracțiilor zecimale finite", "Addition and subtraction of finite decimal fractions"),
            ("Înmulțirea fracțiilor zecimale finite; puterea cu exponent natural", "Multiplication; powers with natural exponent"),
            ("Împărțirea unei fracții zecimale la un număr natural nenul", "Dividing a decimal fraction by a nonzero natural number"),
            ("Împărțirea a două fracții zecimale finite nenule", "Dividing two nonzero finite decimal fractions"),
            ("Transformări între fracții ordinare și zecimale; fracții zecimale periodice", "Conversions between ordinary and decimal fractions; periodic decimals"),
            ("Media aritmetică; număr rațional pozitiv; ordinea operațiilor cu numere raționale pozitive", "Arithmetic mean; positive rational numbers; order of operations"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 50, "exercise_count": 15},
    },
    {
        "order": 6,
        "title": "Probleme Practice",
        "description": "Practical Problems — fraction word problems, data organization, statistics.",
        "lessons": [
            ("Metode aritmetice pentru rezolvarea problemelor cu fracții", "Arithmetic methods for fraction problems"),
            ("Probleme de organizarea datelor; frecvență; date statistice în tabele și grafice", "Data organization; frequency; statistical data in tables and graphs"),
            ("Media unui set de date statistice", "Mean of a statistical data set"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 40, "exercise_count": 10},
    },
    {
        "order": 7,
        "title": "Elemente de Geometrie",
        "description": "Geometry Elements — points, lines, segments, angles, symmetry.",
        "lessons": [
            ("Punct, dreaptă, plan, semidreaptă, segment; poziții relative", "Points, lines, planes, rays, segments; relative positions"),
            ("Lungimea unui segment; segmente congruente; mijlocul segmentului", "Segment length; congruent segments; midpoint"),
            ("Unghiul: definiție, măsură, unghiuri congruente", "Angles: definition, measurement, congruent angles"),
            ("Clasificări de unghiuri: drept, ascuțit, obtuz, nul, alungit", "Angle classification: right, acute, obtuse, null, straight"),
            ("Calcule cu măsuri de unghiuri în grade și minute sexagesimale", "Calculations with angle measures in degrees and minutes"),
            ("Figuri congruente; simetria față de o dreaptă; axa de simetrie", "Congruent figures; line symmetry; axis of symmetry"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 45, "exercise_count": 12},
    },
    {
        "order": 8,
        "title": "Unități de Măsură",
        "description": "Units of Measurement — length, area, volume; conversions and applications.",
        "lessons": [
            ("Unități de măsură pentru lungime; transformări; calcul de perimetre", "Length units; conversions; perimeter calculations"),
            ("Unități de măsură pentru arie; aria pătratului și dreptunghiului; transformări", "Area units; square and rectangle area; conversions"),
            ("Unități de măsură pentru volum; volumul cubului și paralelipipedului dreptunghic; transformări", "Volume units; cube and rectangular parallelepiped volume; conversions"),
            ("Aplicații complexe cu unități de măsură", "Complex applications with units of measurement"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 45, "exercise_count": 12},
    },
]


class Command(BaseCommand):
    help = "Seeds the Grade 5 curriculum structure (8 units, ~33 lessons, 8 tests)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing Grade 5 data before seeding",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing existing Grade 5 data...")
            Grade.objects.filter(number=5).delete()

        # Create or get Grade 5
        grade, created = Grade.objects.get_or_create(
            number=5,
            defaults={"name": "Clasa a V-a", "is_active": True},
        )
        if not created:
            self.stdout.write(self.style.WARNING("Grade 5 already exists. Updating..."))
            grade.is_active = True
            grade.save()

        total_lessons = 0
        total_tests = 0

        for unit_data in GRADE_5_CURRICULUM:
            unit, u_created = Unit.objects.get_or_create(
                grade=grade,
                order=unit_data["order"],
                defaults={
                    "title": unit_data["title"],
                    "description": unit_data["description"],
                    "is_published": True,
                },
            )
            action = "Created" if u_created else "Found"
            self.stdout.write(f"  {action} Unit {unit_data['order']}: {unit_data['title']}")

            # Create lessons
            for idx, (title_ro, summary_en) in enumerate(unit_data["lessons"], start=1):
                lesson, l_created = Lesson.objects.get_or_create(
                    unit=unit,
                    order=idx,
                    defaults={
                        "title": title_ro,
                        "summary": summary_en,
                        "content": f"# {title_ro}\n\nConținut în curs de elaborare.",
                        "is_published": False,  # Not published until content is written
                        "practice_minimum": 5,
                    },
                )
                if l_created:
                    total_lessons += 1

            # Create test
            test_config = unit_data["test"]
            test, t_created = Test.objects.get_or_create(
                unit=unit,
                defaults={
                    "pass_threshold": test_config["pass_threshold"],
                    "time_limit_minutes": test_config["time_limit_minutes"],
                    "exercise_count": test_config["exercise_count"],
                    "is_published": False,
                },
            )
            if t_created:
                total_tests += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! Created {total_lessons} lessons and {total_tests} tests "
                f"across {len(GRADE_5_CURRICULUM)} units for Grade 5."
            )
        )
