"""
Exercise instance generator for MathEd Romania.

Takes an Exercise's JSONB template and returns a concrete instance
with randomized parameter values ready to send to the frontend.

The generated params are signed with Django's signing framework and
returned as an opaque `instance_token`. The token is sent back by the
frontend when submitting an answer so we can grade correctly without
storing per-session state in the DB.

─── JSONB template format ───────────────────────────────────────────

Every template must have a "params" key (can be empty {}) and a type-
specific set of fields. Examples for each exercise type are documented
inline below.

fill_blank
──────────
{
  "type": "fill_blank",
  "question": "Calculați: {a} + {b}",
  "params": {
    "a": {"type": "randint", "min": 100, "max": 999},
    "b": {"type": "randint", "min": 100, "max": 999}
  },
  "answer_expr": "{a} + {b}",
  "answer_input": "number",         // "number" | "expression"
  "placeholder": "Răspuns...",      // optional
  "hint": "Adunați cele două numere"  // optional
}

multiple_choice
───────────────
{
  "type": "multiple_choice",
  "question": "Care este produsul lui {a} și {b}?",
  "params": {
    "a": {"type": "randint", "min": 10, "max": 50},
    "b": {"type": "randint", "min": 10, "max": 50}
  },
  "options": [
    {"id": "A", "text": "{a} * {b}",         "is_correct": true},
    {"id": "B", "text": "{a} * {b} + {d1}",  "is_correct": false},
    {"id": "C", "text": "{a} * {b} - {d2}",  "is_correct": false},
    {"id": "D", "text": "{a} + {b}",         "is_correct": false}
  ],
  "distractor_params": {
    "d1": {"type": "randint", "min": 1, "max": 9},
    "d2": {"type": "randint", "min": 1, "max": 9}
  }
}

comparison
──────────
{
  "type": "comparison",
  "question": "Comparați numerele:",
  "params": {
    "a": {"type": "randint", "min": 2, "max": 20},
    "n": {"type": "randint", "min": 2, "max": 8},
    "m": {"type": "randint", "min": 2, "max": 8}
  },
  "left":  "{a}^{n}",
  "right": "{a}^{m}"
}

drag_order
──────────
{
  "type": "drag_order",
  "question": "Ordonați crescător:",
  "params": {
    "a": {"type": "randint", "min": 100, "max": 999},
    "b": {"type": "randint", "min": 100, "max": 999},
    "c": {"type": "randint", "min": 100, "max": 999},
    "d": {"type": "randint", "min": 100, "max": 999}
  },
  "items": ["{a}", "{b}", "{c}", "{d}"],
  "order_direction": "ascending"    // "ascending" | "descending"
}
"""
import random
from typing import Any
from math import factorial
import re

from django.core import signing

# Salt used when signing instance tokens — change to invalidate all tokens.
_TOKEN_SALT = "mathed-exercise-instance-v1"


# ─── Parameter generators ─────────────────────────────────────────────────────

def _generate_params(params_spec: dict) -> dict:
    """
    Resolve all param specs into concrete values.

    Supports four types:
      randint       — random integer between min and max (both can be expressions)
      randint_nonzero — same but never zero
      choice        — random element from a list
      fixed         — constant value
      computed      — Python expression evaluated after all others are resolved
      label         — maps a resolved param's value to a display string

    Dependency resolution:
      - Passes 1 & 2 retry until all non-computed/non-label params resolve,
        so a randint whose bounds reference another randint works correctly.
      - Pass 3 retries computed params until all chain dependencies resolve,
        so computed params can depend on other computed params (e.g. x → a, b).
      - Pass 4 resolves labels last, after everything else is settled.
    """
    result: dict[str, Any] = {}

    def _eval_expr(expr, current: dict) -> int:
        """Substitute resolved params into an expression string and eval it."""
        s = str(expr)
        for k, v in current.items():
            s = s.replace(f"{{{k}}}", str(v))
        return int(eval(s))  # safe: only math ops on integers

    # ── Passes 1 & 2: resolve randint / choice / fixed (with retry) ──────────
    simple_types = {"randint", "randint_nonzero", "choice", "fixed"}
    pending = {n: s for n, s in params_spec.items() if s["type"] in simple_types}

    max_iterations = len(pending) + 1
    for _ in range(max_iterations):
        if not pending:
            break
        made_progress = False
        for name, spec in list(pending.items()):
            if name in result:
                del pending[name]
                continue
            t = spec["type"]
            try:
                if t == "randint":
                    lo = _eval_expr(spec["min"], result)
                    hi = _eval_expr(spec["max"], result)
                    result[name] = random.randint(lo, hi)
                elif t == "randint_nonzero":
                    lo = _eval_expr(spec["min"], result)
                    hi = _eval_expr(spec["max"], result)
                    v = 0
                    while v == 0:
                        v = random.randint(lo, hi)
                    result[name] = v
                elif t == "choice":
                    result[name] = random.choice(spec["options"])
                elif t == "fixed":
                    result[name] = spec["value"]
                del pending[name]
                made_progress = True
            except (KeyError, NameError, ValueError):
                # A bound references a param not yet resolved — retry next round
                continue
        if not made_progress:
            # Remaining params have unresolvable dependencies
            unresolved = list(pending.keys())
            raise ValueError(f"Cannot resolve params (circular or missing dependency): {unresolved}")

    # ── Pass 3: computed params (retry until all chain dependencies resolve) ──
    computed = {n: s for n, s in params_spec.items() if s["type"] == "computed"}
    max_iterations = len(computed) + 1
    for _ in range(max_iterations):
        if all(n in result for n in computed):
            break
        made_progress = False
        for name, spec in computed.items():
            if name in result:
                continue
            try:
                result[name] = _eval_expr(spec["expr"], result)
                made_progress = True
            except (KeyError, NameError, ValueError):
                continue  # dependency not yet resolved — retry
        if not made_progress:
            unresolved = [n for n in computed if n not in result]
            raise ValueError(f"Cannot resolve computed params (circular or missing dependency): {unresolved}")

    # ── Pass 4: label params (always last — source must already be resolved) ──
    for name, spec in params_spec.items():
        if spec["type"] != "label":
            continue
        source_val = str(result[spec["source"]])
        mapping = spec["map"]
        if source_val not in mapping:
            raise ValueError(f"Label param '{name}': no mapping for value '{source_val}'")
        result[name] = mapping[source_val]

    return result


def _fill(template_str: str, params: dict) -> str:
    """Replace {param_name} placeholders with concrete values."""
    result = template_str
    for key, value in params.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result


def _to_katex(expr: str) -> str:
    """
    Convert a Python-style arithmetic expression to a KaTeX-renderable form.

    Handles:
      - `a**b`       →  `a^{b}`       (works for digits, parenthesized exps)
      - `a * b`      →  `a \\cdot b`
      - `a : b`      →  `a : b`       (left as-is — Romanian division)
      - Parentheses, digits, and variables pass through.

    Examples:
      >>> _to_katex("2**100")
      '2^{100}'
      >>> _to_katex("2**(n+1) + 2**n")
      '2^{n+1} + 2^{n}'
      >>> _to_katex("3 * 2**n")
      '3 \\cdot 2^{n}'
    """
    s = expr

    # ** (parenthesized exponent):  a**(expr)  →  a^{expr}
    s = re.sub(r"\*\*\(([^()]*)\)", r"^{\1}", s)
    # ** (bare exponent):            a**123     →  a^{123}
    s = re.sub(r"\*\*([A-Za-z0-9_]+)", r"^{\1}", s)

    # Multiplication: * → \cdot (with spaces preserved)
    s = re.sub(r"\s*\*\s*", r" \\cdot ", s)

    return s

# ─── Per-type instance builders ───────────────────────────────────────────────

def _build_fill_blank(template: dict, params: dict) -> tuple[dict, dict]:
    frontend = {
        "question": _fill(template["question"], params),
        "answer_input": template.get("answer_input", "expression"),
        "hint": template.get("hint"),
        "placeholder": template.get("placeholder", "Răspuns..."),
    }

    # ── Set-membership grading ────────────────────────────────────────────
    if "valid_set_expr" in template:
        expr = _fill(template["valid_set_expr"], params)
        valid_set = list(eval(expr, {"__builtins__": {}}, {"range": range}))
        grading = {
            "valid_set": valid_set,
            "answer_display": template.get("answer_display", ""),
        }
    else:
        grading = {
            "correct_expr": _fill(template["answer_expr"], params),
        }

    # ── Follow-up mode: two valid answers ────────────────────────────────
    if "alt_answer_expr" in template:
        alt_expr = _fill(template["alt_answer_expr"], params)
        grading = {
            "correct_exprs": [_fill(template["answer_expr"], params), alt_expr],
            "follow_up_question": _fill(template.get("follow_up_question", ""), params),
        }
        frontend["display_mode"] = "follow_up"
        frontend["follow_up_question"] = _fill(template.get("follow_up_question", ""), params)

    return frontend, grading


def _build_multi_fill_blank(template: dict, params: dict) -> tuple[dict, dict]:
    """
    Multi-field fill-in-the-blank. Student fills in one input per field.
    All fields must be correct for the attempt to count as correct.

    Template format:
    {
      "question": "Determinați cifrele $a, b, c, d$ știind că ...",
      "params": { ... },
      "fields": [
        {"key": "a", "label": "a", "answer_expr": "{p}"},
        ...
      ],
      "hint": "...",
      "display_mode": "inline_between",        // optional
      "between_value": "{n}"                   // required when display_mode="inline_between"
    }
    """
    fields_out = []
    correct_map = {}

    for field in template["fields"]:
        key = field["key"]
        label = field["label"]
        correct_expr = _fill(field["answer_expr"], params)
        fields_out.append({"key": key, "label": label})
        correct_map[key] = correct_expr

    frontend = {
        "question": _fill(template["question"], params),
        "fields": fields_out,
        "hint": template.get("hint"),
    }

    # Pass through display_mode + resolved between_value if present
    if template.get("display_mode"):
        frontend["display_mode"] = template["display_mode"]
    if "between_value" in template:
        frontend["between_value"] = _fill(template["between_value"], params)

    grading = {
        "correct_map": correct_map,
    }
    return frontend, grading


def _build_multiple_choice(template: dict, params: dict) -> tuple[dict, dict]:
    # ── Digit click: number IS the UI, no option boxes ──────────────────────
    if template.get("display_mode") == "digit_click":
        n = str(params["n"])
        correct_position = template["correct_position"]
        position_name = template.get("position_name", "")
        question = _fill(template["question"], params)
        question = question.replace("{position_name}", position_name)

        frontend = {
            "question": question,
            "display_mode": "digit_click",
            "number_string": n,
            "options": [],  # unused in this mode
        }
        grading = {
            "correct_option_id": str(correct_position),
        }
        return frontend, grading

    # ── Standard multiple choice ─────────────────────────────────────────────
    all_params = {**params}
    dist_spec = template.get("distractor_params", {})
    dist_params = _generate_params(dist_spec)
    all_params.update(dist_params)

    options_out = []
    correct_id = None
    seen_values = set()

    for opt in template["options"]:
        filled_text = _fill(opt["text"], all_params)
        if filled_text in seen_values:
            continue
        seen_values.add(filled_text)
        options_out.append({"id": opt["id"], "text": filled_text})
        if opt.get("is_correct"):
            correct_id = opt["id"]

    random.shuffle(options_out)

    question = _fill(template["question"], all_params)
    if "position_name" in template:
        question = question.replace("{position_name}", template["position_name"])

    frontend = {
        "question": question,
        "options": options_out,
        "display_mode": template.get("display_mode"),
    }
    grading = {"correct_option_id": correct_id}
    return frontend, grading


def _build_comparison(template: dict, params: dict) -> tuple[dict, dict]:
    """Build comparison (<, =, >) instance."""
    left = _fill(template["left"], params)
    right = _fill(template["right"], params)

    frontend = {
        "question": template.get("question", "Comparați numerele:"),
        "left": _to_katex(left),  # ← KaTeX for display
        "right": _to_katex(right),  # ← KaTeX for display
        "options": [
            {"id": "<", "text": "<"},
            {"id": "=", "text": "="},
            {"id": ">", "text": ">"},
        ],
    }
    grading = {
        "left_expr": left,  # ← keep Python syntax for SymPy
        "right_expr": right,
    }
    return frontend, grading


def _build_drag_order(template: dict, params: dict) -> tuple[dict, dict]:
    """Build drag-to-order instance."""
    items_filled = [_fill(item, params) for item in template["items"]]
    direction = template.get("order_direction", "ascending")

    # Determine correct order using Python-evaluable form (so 2**40 sorts correctly).
    def sort_key(x: str):
        try:
            return (0, eval(x, {"__builtins__": {}}))
        except Exception:
            try:
                return (0, int(x))
            except ValueError:
                return (1, x)

    correct_order = sorted(
        items_filled,
        key=sort_key,
        reverse=(direction == "descending"),
    )

    # Shuffle for display
    display_items = items_filled.copy()
    random.shuffle(display_items)
    attempts = 0
    while display_items == correct_order and attempts < 10:
        random.shuffle(display_items)
        attempts += 1

    # Convert to KaTeX for display (grading uses original strings).
    frontend = {
        "question": _fill(template.get("question", "Ordonați:"), params),
        "items": [_to_katex(item) for item in display_items],
        "order_direction": direction,
    }
    grading = {
        "correct_order": [_to_katex(item) for item in correct_order],
    }
    return frontend, grading


# ─── Public API ───────────────────────────────────────────────────────────────

def generate_instance(exercise) -> dict:
    """
    Generate a concrete, randomized exercise instance from an Exercise model.

    Returns a dict safe to send to the frontend. The `instance_token` field
    is a signed blob containing everything needed to grade the submission
    later — the frontend must echo it back in the attempt request.

    Raises ValueError if the template is malformed.
    """
    template = exercise.template
    exercise_type = exercise.exercise_type

    params_spec = template.get("params", {})
    params = _generate_params(params_spec)

    builders = {
        "fill_blank": _build_fill_blank,
        "multi_fill_blank": _build_multi_fill_blank,
        "multiple_choice": _build_multiple_choice,

        "comparison": _build_comparison,
        "drag_order": _build_drag_order,
    }

    if exercise_type not in builders:
        raise ValueError(f"Unsupported exercise type: {exercise_type}")

    frontend_data, grading_data = builders[exercise_type](template, params)

    # Sign the grading data so it cannot be tampered with.
    instance_token = signing.dumps(
        {
            "exercise_id": exercise.id,
            "exercise_type": exercise_type,
            "grading_data": grading_data,
            "nonce": random.randint(0, 999999),
        },
        salt=_TOKEN_SALT,
    )

    instance = {
        "exercise_id": exercise.id,
        "exercise_type": exercise_type,
        "difficulty": exercise.difficulty,
        "instance_token": instance_token,
        **frontend_data,
    }

    # Pass through display_mode if set in template
    if "display_mode" in template:
        instance["display_mode"] = template["display_mode"]

    return instance


def decode_instance_token(token: str) -> dict:
    """
    Decode and verify a signed instance token.

    Returns the payload dict with keys: exercise_id, exercise_type, grading_data.
    Raises signing.BadSignature if tampered, signing.SignatureExpired if older than 1 hour.
    """
    return signing.loads(token, salt=_TOKEN_SALT, max_age=3600)
