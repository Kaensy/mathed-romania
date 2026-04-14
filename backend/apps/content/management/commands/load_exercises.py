"""
Bulk-load exercises into the database from structured Python data files.

Usage:
    python manage.py load_exercises exercises.addition_compute
    python manage.py load_exercises exercises.find_x_addition
    python manage.py load_exercises exercises.addition_compute exercises.find_x_addition
    python manage.py load_exercises --all
    python manage.py load_exercises exercises.addition_compute --flush

Data files live in backend/exercises/ and export an EXERCISES list.
Each entry specifies the template, difficulty, category, and topic lookup.
"""
import importlib

from django.core.management.base import BaseCommand, CommandError

from apps.content.models import Exercise, Topic


# All known exercise data modules (used by --all flag)
ALL_MODULES = [
    # 1.4 - Adunare
    "exercises.addition_compute",
    "exercises.find_x_addition",
    "exercises.gauss_sum",
    "exercises.arithmetic_sequence",

    # 1.5 - Scadere
    "exercises.subtraction_compute",
    "exercises.find_x_subtraction",
    "exercises.sum_and_difference",

    # 1.6 - Inmultire
    "exercises.multiplication_compute",
    "exercises.find_x_multiplication",
    "exercises.common_factor",

    # 1.7 - Impartire
    "exercises.division_compute",
    "exercises.find_x_division",
    "exercises.division_remainder_compute",
    "exercises.find_from_division_theorem",

    # 1.8 - Puteri
    "exercises.power_notation",
    "exercises.power_compute",
    "exercises.power_rules_simplify",
    "exercises.power_common_factor",
    "exercises.find_x_powers",
    "exercises.power_last_digit",
    "exercises.power_sum_telescope",
    "exercises.power_compare",
    "exercises.power_order",
    "exercises.perfect_square_identify",
    "exercises.perfect_square_between",

    # 1.9 - Baze de numeratie
    "exercises.convert_to_base10",
    "exercises.convert_from_base10",
    "exercises.mixed_base_compute",

    # 1.10 - Ordinea operatiilor
    "exercises.order_of_ops_basic",
    "exercises.order_of_ops_parens",
    "exercises.order_of_ops_nested",


    # Add new modules here as they're created
]


class Command(BaseCommand):
    help = "Bulk-load exercises from structured Python data files in backend/exercises/"

    def add_arguments(self, parser):
        parser.add_argument(
            "modules",
            nargs="*",
            help="Dotted module paths to exercise data files (e.g., exercises.addition_compute)",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Load all known exercise modules",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing exercises for the same topic+category before loading",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without touching the database",
        )

    def handle(self, *args, **options):
        modules = options["modules"]
        if options["all"]:
            modules = ALL_MODULES
        if not modules:
            raise CommandError(
                "Specify at least one module path (e.g., exercises.addition_compute) or use --all"
            )

        total_created = 0
        total_skipped = 0
        total_flushed = 0

        for module_path in modules:
            self.stdout.write(f"\n{'═' * 60}")
            self.stdout.write(f"  Loading: {module_path}")
            self.stdout.write(f"{'═' * 60}")

            try:
                mod = importlib.import_module(module_path)
            except ImportError as e:
                self.stderr.write(self.style.ERROR(f"  Cannot import {module_path}: {e}"))
                continue

            if not hasattr(mod, "EXERCISES"):
                self.stderr.write(self.style.ERROR(f"  {module_path} has no EXERCISES list"))
                continue

            exercises_data = mod.EXERCISES

            # ── Resolve topic ────────────────────────────────────────────
            topic_ref = getattr(mod, "TOPIC", None)
            if not topic_ref:
                self.stderr.write(self.style.ERROR(f"  {module_path} has no TOPIC dict"))
                continue

            topic = self._resolve_topic(topic_ref)
            if not topic:
                continue

            self.stdout.write(f"  Topic: {topic}")

            # ── Flush if requested ───────────────────────────────────────
            if options["flush"]:
                categories = {ex["category"] for ex in exercises_data}
                for cat in categories:
                    qs = Exercise.objects.filter(topic=topic, category=cat)
                    count = qs.count()
                    if count and not options["dry_run"]:
                        qs.delete()
                    total_flushed += count
                    if count:
                        self.stdout.write(
                            self.style.WARNING(f"  Flushed {count} existing '{cat}' exercises")
                        )

            # ── Create exercises ─────────────────────────────────────────
            for i, ex_data in enumerate(exercises_data, 1):
                name = ex_data.get("name", f"Exercise {i}")
                category = ex_data["category"]
                difficulty = ex_data["difficulty"]
                exercise_type = ex_data["exercise_type"]
                template = ex_data["template"]

                # Check for duplicates using the template title (unique per exercise).
                # Falls back to question string if no title is set.
                title = template.get("title", "")
                if title:
                    exists = Exercise.objects.filter(
                        topic=topic,
                        category=category,
                        template__title=title,
                    ).exists()
                else:
                    question_tpl = template.get("question", "")
                    exists = Exercise.objects.filter(
                        topic=topic,
                        category=category,
                        difficulty=difficulty,
                        exercise_type=exercise_type,
                        template__question=question_tpl,
                    ).exists()

                if exists and not options["flush"]:
                    self.stdout.write(f"  ⏭  {name} [{difficulty}] — already exists, skipping")
                    total_skipped += 1
                    continue

                if options["dry_run"]:
                    self.stdout.write(f"  🔍 {name} [{difficulty}] — would create")
                    total_created += 1
                    continue

                Exercise.objects.create(
                    topic=topic,
                    exercise_type=exercise_type,
                    difficulty=difficulty,
                    category=category,
                    template=template,
                    is_active=True,
                )
                self.stdout.write(self.style.SUCCESS(f"  ✅ {name} [{difficulty}]"))
                total_created += 1

        # ── Summary ──────────────────────────────────────────────────────
        self.stdout.write(f"\n{'═' * 60}")
        action = "Would create" if options["dry_run"] else "Created"
        self.stdout.write(
            self.style.SUCCESS(
                f"  {action} {total_created} exercises, "
                f"skipped {total_skipped}, flushed {total_flushed}"
            )
        )
        self.stdout.write(f"{'═' * 60}\n")

    def _resolve_topic(self, topic_ref: dict):
        """
        Resolve a topic reference dict to a Topic model instance.

        Supports two lookup modes:
          {"grade": 5, "unit_order": 1, "topic_order": 4}
          {"topic_id": 42}
        """
        if "topic_id" in topic_ref:
            try:
                return Topic.objects.get(id=topic_ref["topic_id"])
            except Topic.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"  Topic id={topic_ref['topic_id']} not found")
                )
                return None

        grade = topic_ref.get("grade")
        unit_order = topic_ref.get("unit_order")
        topic_order = topic_ref.get("topic_order")

        try:
            return Topic.objects.get(
                unit__grade__number=grade,
                unit__order=unit_order,
                order=topic_order,
            )
        except Topic.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    f"  Topic not found: grade={grade}, unit={unit_order}, topic={topic_order}"
                )
            )
            return None
        except Topic.MultipleObjectsReturned:
            self.stderr.write(
                self.style.ERROR(
                    f"  Multiple topics match: grade={grade}, unit={unit_order}, topic={topic_order}"
                )
            )
            return None