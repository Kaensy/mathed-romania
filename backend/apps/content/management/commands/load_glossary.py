"""
Bulk-load glossary terms into the database from structured Python data files.

Usage:
    python manage.py load_glossary glossary.grade5_unit1
    python manage.py load_glossary glossary.grade5_unit1 glossary.grade5_unit2
    python manage.py load_glossary --all
    python manage.py load_glossary glossary.grade5_unit1 --flush

Data files live in backend/glossary/ (one per unit) and export:
    UNIT  — {"grade": int, "order": int} resolving the Unit FK
    TERMS — list of dicts with keys: term, aliases, definition, category, examples
"""
import importlib

from django.core.management.base import BaseCommand, CommandError

from apps.content.models import GlossaryTerm, Unit

# All known glossary data modules (used by --all flag)
ALL_MODULES = [
    "glossary.grade5_unit1",

    # Add new modules here as they're created
]


VALID_CATEGORIES = {choice for choice, _ in GlossaryTerm.Category.choices}


class Command(BaseCommand):
    help = "Bulk-load glossary terms from structured Python data files in backend/glossary/"

    def add_arguments(self, parser):
        parser.add_argument(
            "modules",
            nargs="*",
            help="Dotted module paths to glossary data files (e.g., glossary.grade5_unit1)",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Load all known glossary modules",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all glossary terms scoped to the resolved unit before loading",
        )

    def handle(self, *args, **options):
        modules = options["modules"]
        if options["all"]:
            modules = ALL_MODULES
        if not modules:
            raise CommandError(
                "Specify at least one module path (e.g., glossary.grade5_unit1) or use --all"
            )

        grand_created = 0
        grand_updated = 0
        grand_skipped = 0
        grand_flushed = 0

        for module_path in modules:
            self.stdout.write(f"\n{'═' * 60}")
            self.stdout.write(f"  Loading: {module_path}")
            self.stdout.write(f"{'═' * 60}")

            try:
                mod = importlib.import_module(module_path)
            except ImportError as e:
                raise CommandError(f"Cannot import {module_path}: {e}")

            if not hasattr(mod, "UNIT"):
                raise CommandError(f"{module_path} has no UNIT dict")
            if not hasattr(mod, "TERMS"):
                raise CommandError(f"{module_path} has no TERMS list")

            unit = self._resolve_unit(module_path, mod.UNIT)
            self.stdout.write(f"  Unit: {unit}")

            errors = self._validate_terms(module_path, unit, mod.TERMS)
            if errors:
                for msg in errors:
                    self.stderr.write(self.style.ERROR(msg))
                raise CommandError(
                    f"{module_path}: validation failed with {len(errors)} error(s)"
                )

            if options["flush"]:
                qs = GlossaryTerm.objects.filter(unit=unit)
                count = qs.count()
                if count:
                    qs.delete()
                    grand_flushed += count
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Flushed {count} existing term(s) in {unit}"
                        )
                    )

            created, updated, skipped = self._upsert_terms(unit, mod.TERMS)
            grand_created += created
            grand_updated += updated
            grand_skipped += skipped

            self.stdout.write(
                self.style.SUCCESS(
                    f"  {module_path}: created {created}, updated {updated}, skipped {skipped}"
                )
            )

        self.stdout.write(f"\n{'═' * 60}")
        self.stdout.write(
            self.style.SUCCESS(
                f"  Total: created {grand_created}, updated {grand_updated}, "
                f"skipped {grand_skipped}, flushed {grand_flushed}"
            )
        )
        self.stdout.write(f"{'═' * 60}\n")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _resolve_unit(self, module_path: str, unit_ref: dict) -> Unit:
        grade = unit_ref.get("grade")
        order = unit_ref.get("order")
        if grade is None or order is None:
            raise CommandError(
                f"{module_path}: UNIT must have both 'grade' and 'order' keys"
            )
        try:
            return Unit.objects.get(grade__number=grade, order=order)
        except Unit.DoesNotExist:
            raise CommandError(
                f"{module_path}: Unit not found for grade={grade}, order={order}"
            )

    def _validate_terms(
        self, module_path: str, unit: Unit, terms: list
    ) -> list[str]:
        """Return a list of human-readable error messages; empty list means OK."""
        errors: list[str] = []
        seen_in_file: dict[str, int] = {}

        for idx, raw in enumerate(terms):
            ctx = f"  ✗ {module_path} TERMS[{idx}]"

            if not isinstance(raw, dict):
                errors.append(f"{ctx}: entry is not a dict")
                continue

            term_value = raw.get("term", "")
            if not isinstance(term_value, str):
                errors.append(f"{ctx}: 'term' must be a string")
                continue
            term_stripped = term_value.strip()
            if not term_stripped:
                errors.append(f"{ctx}: 'term' is required and must be non-empty")
                continue

            label = f"{ctx} ('{term_stripped}')"

            if term_stripped in seen_in_file:
                errors.append(
                    f"{label}: duplicate of TERMS[{seen_in_file[term_stripped]}]"
                )
            else:
                seen_in_file[term_stripped] = idx

            aliases = raw.get("aliases", [])
            if not isinstance(aliases, list) or not all(
                isinstance(a, str) for a in aliases
            ):
                errors.append(f"{label}: 'aliases' must be a list of strings")

            examples = raw.get("examples", [])
            if not isinstance(examples, list) or not all(
                isinstance(e, str) for e in examples
            ):
                errors.append(f"{label}: 'examples' must be a list of strings")

            category = raw.get("category", GlossaryTerm.Category.DEFINITION)
            if category not in VALID_CATEGORIES:
                errors.append(
                    f"{label}: 'category' must be one of {sorted(VALID_CATEGORIES)}, got {category!r}"
                )

            if "definition" not in raw or not isinstance(raw["definition"], str):
                errors.append(f"{label}: 'definition' is required and must be a string")

            existing = (
                GlossaryTerm.objects.filter(term=term_stripped)
                .exclude(unit=unit)
                .first()
            )
            if existing is not None:
                errors.append(
                    f"{label}: already exists in DB under {existing.unit} "
                    f"— move it manually or rename"
                )

        return errors

    def _upsert_terms(self, unit: Unit, terms: list) -> tuple[int, int, int]:
        created = updated = skipped = 0

        for raw in terms:
            term_value = raw["term"].strip()
            payload = {
                "definition": raw["definition"],
                "aliases": list(raw.get("aliases", [])),
                "examples": list(raw.get("examples", [])),
                "category": raw.get("category", GlossaryTerm.Category.DEFINITION),
                "unit": unit,
            }

            existing = GlossaryTerm.objects.filter(term=term_value).first()
            if existing is None:
                GlossaryTerm.objects.create(term=term_value, **payload)
                self.stdout.write(self.style.SUCCESS(f"  ✅ {term_value}"))
                created += 1
                continue

            changed_fields = [
                f for f in ("definition", "aliases", "examples", "category")
                if getattr(existing, f) != payload[f]
            ]
            if not changed_fields:
                self.stdout.write(f"  ⏭  {term_value} — no changes")
                skipped += 1
                continue

            for field in changed_fields:
                setattr(existing, field, payload[field])
            existing.save(update_fields=changed_fields + ["updated_at"])
            self.stdout.write(
                self.style.WARNING(
                    f"  ✏  {term_value} — updated ({', '.join(changed_fields)})"
                )
            )
            updated += 1

        return created, updated, skipped
