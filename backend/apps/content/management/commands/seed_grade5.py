"""
Seeds the Grade 5 curriculum structure based

Creates: 1 Grade, 8 Units, Topics (one per lesson), Lessons, 8 Unit Tests.

After running this seed, use Django admin to:
  1. Merge split topics (e.g. combine lesson-4 and lesson-5 topics into
     one "Adunarea numerelor naturale" topic for Unit 1)
  2. Set topic titles for merged topics
  3. Publish topics as content is ready

"""
from django.core.management.base import BaseCommand

from apps.content.models import Grade, Lesson, Test, Topic, Unit


# Full Grade 5 curriculum
GRADE_5_CURRICULUM = [
    {
        "order": 1,
        "title": "Numere Naturale",
        "description": "Natural Numbers — operations, properties, powers, number bases, order of operations.",
        "lessons": [
            ("Scrierea și citirea numerelor naturale", "Writing and reading natural numbers"),
            ("Reprezentarea pe axa numerelor; compararea și ordonarea", "Number line representation; comparing and ordering"),
            ("Aproximări și probleme de estimare", "Approximations and estimation problems"),
            ("Adunarea numerelor naturale: calcul și proprietăți", "Addition of natural numbers; properties"),
            ("Adunarea numerelor naturale: suma lui Gauss", "Addition: Gauss sum and arithmetic sequences"),
            ("Scăderea numerelor naturale", "Subtraction of natural numbers"),
            ("Înmulțirea numerelor naturale: calcul și proprietăți", "Multiplication: calculation and properties"),
            ("Înmulțirea numerelor naturale: distributivitate și factori comuni", "Multiplication: distributivity and common factors"),
            ("Împărțirea exactă a numerelor naturale", "Exact division of natural numbers"),
            ("Împărțirea cu rest", "Division with remainder; division theorem"),
            ("Puterea cu exponent natural: definiție și reguli de calcul", "Powers: definition and calculation rules"),
            ("Puterea cu exponent natural: ultima cifră și suma puterilor", "Powers: last digit and sum of powers"),
            ("Puterea cu exponent natural: compararea și pătrate perfecte", "Powers: comparing and perfect squares"),
            ("Baze de numerație: scrierea în baza 10 și baza 2", "Number bases: writing in base 10 and base 2"),
            ("Ordinea efectuării operațiilor", "Order of operations"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 45},
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
        "test": {"pass_threshold": 70, "time_limit_minutes": 40},
    },
    {
        "order": 3,
        "title": "Divizibilitatea Numerelor Naturale",
        "description": "Divisibility of Natural Numbers — divisors, multiples, divisibility criteria, primes.",
        "lessons": [
            ("Mulțimea divizorilor și mulțimea multiplilor unui număr natural", "Divisors and multiples"),
            ("Criterii de divizibilitate cu 2, 5, 10, 3, 9", "Divisibility criteria"),
            ("Numere prime și numere compuse; descompunerea în factori primi", "Primes; prime factorization"),
            ("Cel mai mare divizor comun (c.m.m.d.c.)", "Greatest common divisor"),
            ("Cel mai mic multiplu comun (c.m.m.m.c.)", "Least common multiple"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 45},
    },
    {
        "order": 4,
        "title": "Fracții",
        "description": "Fractions — concepts, operations, and comparisons.",
        "lessons": [
            ("Fracții; fracții subunitare, echiunitare, supraunitare", "Fractions; sub-unitary, unitary, super-unitary"),
            ("Fracții echivalente; simplificarea și amplificarea fracțiilor", "Equivalent fractions; simplification and amplification"),
            ("Compararea și ordonarea fracțiilor", "Comparing and ordering fractions"),
            ("Adunarea și scăderea fracțiilor", "Addition and subtraction of fractions"),
            ("Înmulțirea fracțiilor", "Multiplication of fractions"),
            ("Împărțirea fracțiilor", "Division of fractions"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 45},
    },
    {
        "order": 5,
        "title": "Numere Raționale Pozitive",
        "description": "Positive Rational Numbers — decimal fractions, operations, and applications.",
        "lessons": [
            ("Fracții zecimale; scrierea și citirea", "Decimal fractions; writing and reading"),
            ("Operații cu fracții zecimale: adunare și scădere", "Operations with decimal fractions: addition and subtraction"),
            ("Operații cu fracții zecimale: înmulțire și împărțire", "Operations: multiplication and division"),
            ("Fracții ordinare și fracții zecimale; conversii", "Ordinary and decimal fractions; conversions"),
            ("Aproximări și rotunjiri ale numerelor raționale pozitive", "Approximations and rounding of positive rationals"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 45},
    },
    {
        "order": 6,
        "title": "Procente",
        "description": "Percentages — concepts, calculations, and applications.",
        "lessons": [
            ("Procentul; semnificație și reprezentare", "Percentages; meaning and representation"),
            ("Calculul procentului dintr-un număr; aflarea numărului când se cunoaște procentul", "Calculating a percentage; finding the number from the percentage"),
            ("Probleme cu procente", "Problems with percentages"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 40},
    },
    {
        "order": 7,
        "title": "Elemente de Geometrie",
        "description": "Geometry — points, lines, angles, symmetry, and congruence.",
        "lessons": [
            ("Punct, dreaptă, plan, semidreaptă, segment; poziții relative", "Points, lines, planes, rays, segments"),
            ("Lungimea unui segment; segmente congruente; mijlocul segmentului", "Segment length; congruent segments; midpoint"),
            ("Unghiul: definiție, măsură, unghiuri congruente", "Angles: definition, measurement, congruent angles"),
            ("Clasificări de unghiuri: drept, ascuțit, obtuz, nul, alungit", "Angle classification"),
            ("Calcule cu măsuri de unghiuri în grade și minute sexagesimale", "Calculations with angle measures"),
            ("Figuri congruente; simetria față de o dreaptă; axa de simetrie", "Congruent figures; line symmetry"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 45},
    },
    {
        "order": 8,
        "title": "Unități de Măsură",
        "description": "Units of Measurement — length, area, volume; conversions and applications.",
        "lessons": [
            ("Unități de măsură pentru lungime; transformări; calcul de perimetre", "Length units; conversions; perimeter calculations"),
            ("Unități de măsură pentru arie; aria pătratului și dreptunghiului", "Area units; square and rectangle area"),
            ("Unități de măsură pentru volum; volumul cubului și paralelipipedului", "Volume units; cube and rectangular parallelepiped volume"),
            ("Aplicații complexe cu unități de măsură", "Complex applications with units of measurement"),
        ],
        "test": {"pass_threshold": 70, "time_limit_minutes": 45},
    },
]


class Command(BaseCommand):
    help = "Seeds the Grade 5 curriculum structure (8 units, 15 topics/lessons for Unit 1, 8 unit tests)"

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

        grade, created = Grade.objects.get_or_create(
            number=5,
            defaults={"name": "Clasa a V-a", "is_active": True},
        )
        if not created:
            self.stdout.write(self.style.WARNING("Grade 5 already exists. Updating..."))
            grade.is_active = True
            grade.save()

        total_topics = 0
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

            # Create one Topic + Lesson per curriculum entry (1-to-1 initially)
            for idx, (title_ro, summary_en) in enumerate(unit_data["lessons"], start=1):
                topic, t_created = Topic.objects.get_or_create(
                    unit=unit,
                    order=idx,
                    defaults={
                        "title": title_ro,
                        "is_published": False,
                        "practice_minimum": 5,
                    },
                )
                if t_created:
                    total_topics += 1

                lesson, l_created = Lesson.objects.get_or_create(
                    topic=topic,
                    order=1,
                    defaults={
                        "title": title_ro,
                        "summary": summary_en,
                        "is_published": False,
                    },
                )
                if l_created:
                    total_lessons += 1

            # Create unit-level test
            test_config = unit_data["test"]
            test, test_created = Test.objects.get_or_create(
                unit=unit,
                defaults={
                    "scope": Test.Scope.UNIT,
                    "pass_threshold": test_config["pass_threshold"],
                    "time_limit_minutes": test_config["time_limit_minutes"],
                    "is_published": False,
                },
            )
            if test_created:
                total_tests += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! Created {total_topics} topics, {total_lessons} lessons, "
                f"and {total_tests} unit tests across {len(GRADE_5_CURRICULUM)} units for Grade 5."
            )
        )
