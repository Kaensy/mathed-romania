"""
XP awards catalog — single source of truth for XP source slugs.

Mirrors the Block 9 badge catalog shape: declarative, self-describing,
adding or editing a source never requires a database migration (XPLedger
stores `source` as a free-form CharField).

Each entry maps a source slug to:
- `amount`: integer XP granted on a successful (non-duplicate) grant.
- `key_builder`: callable taking the call-site context dict and
  returning an `idempotency_key` string. The key_builder decides the
  scope: include a date+grade for daily resets, a topic_id for
  once-per-topic, a category-and-tier for once-per-category-tier, etc.
- `display_name`: Romanian label shown to students in the XP ledger
  history (and other end-user surfaces). Free text — edit freely.

Numbers and labels below are placeholders — tweak freely.
"""
from typing import Callable, TypedDict


class XPAwardDef(TypedDict):
    amount: int
    key_builder: Callable[[dict], str]
    display_name: str


XP_AWARDS: dict[str, XPAwardDef] = {
    # ── Daily (resets each Europe/Bucharest day; ctx requires `date` + `grade_id`) ──
    "daily_first_login": {
        "amount": 5,
        "key_builder": lambda ctx: f"daily_first_login:{ctx['date']}:grade_{ctx['grade_id']}",
        "display_name": "Bun venit zilnic",
    },
    "daily_first_exercise_try": {
        "amount": 5,
        "key_builder": lambda ctx: f"daily_first_exercise_try:{ctx['date']}:grade_{ctx['grade_id']}",
        "display_name": "Prima încercare a zilei",
    },
    "daily_first_exercise_complete": {
        "amount": 10,
        "key_builder": lambda ctx: f"daily_first_exercise_complete:{ctx['date']}:grade_{ctx['grade_id']}",
        "display_name": "Primul exercițiu rezolvat",
    },
    "daily_test_complete": {
        "amount": 30,
        "key_builder": lambda ctx: f"daily_test_complete:{ctx['date']}:grade_{ctx['grade_id']}",
        "display_name": "Test zilnic completat",
    },
    # ── Per-category tier clears (once per (student, category, tier)) ──────────
    "category_easy_tier_cleared": {
        "amount": 25,
        "key_builder": lambda ctx: f"category_easy_tier_cleared:cat_{ctx['category_id']}",
        "display_name": "Nivel ușor cucerit",
    },
    "category_medium_tier_cleared": {
        "amount": 50,
        "key_builder": lambda ctx: f"category_medium_tier_cleared:cat_{ctx['category_id']}",
        "display_name": "Nivel mediu cucerit",
    },
    "category_hard_tier_cleared": {
        "amount": 100,
        "key_builder": lambda ctx: f"category_hard_tier_cleared:cat_{ctx['category_id']}",
        "display_name": "Nivel dificil cucerit",
    },
    # ── Topic / Unit progression (once per topic / unit) ────────────────────────
    "topic_passed": {
        "amount": 50,
        "key_builder": lambda ctx: f"topic_passed:topic_{ctx['topic_id']}",
        "display_name": "Lecție promovată",
    },
    "topic_mastered": {
        "amount": 100,
        "key_builder": lambda ctx: f"topic_mastered:topic_{ctx['topic_id']}",
        "display_name": "Lecție stăpânită",
    },
    "topic_perfect": {
        "amount": 150,
        "key_builder": lambda ctx: f"topic_perfect:topic_{ctx['topic_id']}",
        "display_name": "Lecție perfectă",
    },
    "unit_passed": {
        "amount": 200,
        "key_builder": lambda ctx: f"unit_passed:unit_{ctx['unit_id']}",
        "display_name": "Capitol promovat",
    },
    # ── Discovery (once per resource) ───────────────────────────────────────────
    "lesson_first_open": {
        "amount": 5,
        "key_builder": lambda ctx: f"lesson_first_open:lesson_{ctx['lesson_id']}",
        "display_name": "Lecție nouă deschisă",
    },
}
