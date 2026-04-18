"""
Seed published Test objects for Grade 5, Unit 1:
  - One topic test per topic (scope="topic")
  - One unit test for Unit 1 (scope="unit")

Compositions are derived from the active exercises actually present on
each topic — easy + medium only (hard is reserved for top students).

Idempotent: get_or_create on (scope, topic) / (scope, unit).
Existing tests are left untouched.
"""
from collections import defaultdict

from django.core.management.base import BaseCommand

from apps.content.models import Exercise, Test, Topic, Unit


GRADE_NUMBER = 5
UNIT_ORDER = 1

TOPIC_TEST_PASS_THRESHOLD = 60
UNIT_TEST_PASS_THRESHOLD = 60
UNIT_TEST_TIME_LIMIT_MIN = 45

PER_CATEGORY_COUNT_TOPIC_TEST = 2  # per difficulty, per category
SLOT_WEIGHT = 10


def _category_difficulty_map(topic: Topic) -> dict[str, set[str]]:
    """Return {category: {difficulty, ...}} for active exercises on a topic."""
    cat_diff: dict[str, set[str]] = defaultdict(set)
    for cat, diff in (
        Exercise.objects
        .filter(topic=topic, is_active=True)
        .exclude(category="")
        .values_list("category", "difficulty")
    ):
        cat_diff[cat].add(diff)
    return cat_diff


def _build_topic_composition(topic: Topic) -> list[dict]:
    """Build a topic test composition: 2 easy + 2 medium per category (if available)."""
    composition: list[dict] = []
    cat_diff = _category_difficulty_map(topic)

    for category in sorted(cat_diff.keys()):
        available = cat_diff[category]
        for difficulty in ("easy", "medium"):
            if difficulty in available:
                composition.append({
                    "category": category,
                    "count": PER_CATEGORY_COUNT_TOPIC_TEST,
                    "difficulty": difficulty,
                    "weight": SLOT_WEIGHT,
                })

    return composition


def _build_unit_composition(unit: Unit) -> list[dict]:
    """
    Build a unit test composition: a sampler across all topics in the unit.
    1 easy + 1 medium slot per category that has exercises.
    """
    composition: list[dict] = []

    topics = Topic.objects.filter(unit=unit, is_published=True).order_by("order")
    for topic in topics:
        cat_diff = _category_difficulty_map(topic)
        for category in sorted(cat_diff.keys()):
            available = cat_diff[category]
            for difficulty in ("easy", "medium"):
                if difficulty in available:
                    composition.append({
                        "category": category,
                        "count": 1,
                        "difficulty": difficulty,
                        "weight": SLOT_WEIGHT,
                    })

    return composition


class Command(BaseCommand):
    help = "Seed published topic tests for Unit 1 and a Unit 1 unit test (Grade 5)."

    def handle(self, *args, **options):
        try:
            unit = Unit.objects.select_related("grade").get(
                grade__number=GRADE_NUMBER,
                order=UNIT_ORDER,
            )
        except Unit.DoesNotExist:
            self.stderr.write(self.style.ERROR(
                f"Grade {GRADE_NUMBER} Unit {UNIT_ORDER} not found. Run seed_grade5 first."
            ))
            return

        topics = list(
            Topic.objects.filter(unit=unit).order_by("order")
        )
        self.stdout.write(self.style.NOTICE(
            f"Seeding tests for Grade {GRADE_NUMBER}, Unit {UNIT_ORDER} "
            f"({unit.title}) — {len(topics)} topic(s)"
        ))

        created_topic_tests = 0
        existing_topic_tests = 0
        empty_compositions = 0

        for topic in topics:
            composition = _build_topic_composition(topic)
            if not composition:
                empty_compositions += 1

            _, created = Test.objects.get_or_create(
                topic=topic,
                defaults={
                    "scope": Test.Scope.TOPIC,
                    "composition": composition,
                    "pass_threshold": TOPIC_TEST_PASS_THRESHOLD,
                    "time_limit_minutes": None,
                    "is_published": True,
                },
            )

            if created:
                created_topic_tests += 1
                self.stdout.write(self.style.SUCCESS(
                    f"  + created topic test for T{topic.order} — {topic.title} "
                    f"({len(composition)} slot(s))"
                ))
            else:
                existing_topic_tests += 1
                self.stdout.write(
                    f"  · topic test already exists for T{topic.order} — {topic.title}"
                )

        # Unit test
        unit_composition = _build_unit_composition(unit)
        _, unit_created = Test.objects.get_or_create(
            unit=unit,
            defaults={
                "scope": Test.Scope.UNIT,
                "composition": unit_composition,
                "pass_threshold": UNIT_TEST_PASS_THRESHOLD,
                "time_limit_minutes": UNIT_TEST_TIME_LIMIT_MIN,
                "is_published": True,
            },
        )

        if unit_created:
            self.stdout.write(self.style.SUCCESS(
                f"  + created unit test ({len(unit_composition)} slot(s), "
                f"{UNIT_TEST_TIME_LIMIT_MIN} min)"
            ))
        else:
            self.stdout.write(f"  · unit test already exists for {unit.title}")

        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Summary:"))
        self.stdout.write(f"  Topic tests created: {created_topic_tests}")
        self.stdout.write(f"  Topic tests already present: {existing_topic_tests}")
        self.stdout.write(f"  Topic tests with empty composition: {empty_compositions}")
        self.stdout.write(
            f"  Unit test: {'created' if unit_created else 'already present'}"
        )
