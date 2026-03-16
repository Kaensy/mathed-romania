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

from django.core import signing

# Salt used when signing instance tokens — change to invalidate all tokens.
_TOKEN_SALT = "mathed-exercise-instance-v1"


# ─── Parameter generators ─────────────────────────────────────────────────────

def _generate_params(params_spec: dict) -> dict:
    result: dict[str, Any] = {}
    for name, spec in params_spec.items():
        t = spec["type"]
        if t == "randint":
            result[name] = random.randint(spec["min"], spec["max"])
        elif t == "randint_nonzero":
            v = 0
            while v == 0:
                v = random.randint(spec["min"], spec["max"])
            result[name] = v
        elif t == "choice":
            result[name] = random.choice(spec["options"])
        elif t == "fixed":
            result[name] = spec["value"]
        elif t == "computed":
            # Evaluate a Python expression using already-resolved params.
            # Example: {"type": "computed", "expr": "({n} // 100) % 10"}
            expr = spec["expr"]
            filled = expr
            for key, value in result.items():
                filled = filled.replace(f"{{{key}}}", str(value))
            result[name] = eval(filled)   # safe: only math ops on integers
        else:
            raise ValueError(f"Unknown param type: {t}")
    return result


def _fill(template_str: str, params: dict) -> str:
    """Replace {param_name} placeholders with concrete values."""
    result = template_str
    for key, value in params.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result


# ─── Per-type instance builders ───────────────────────────────────────────────

def _build_fill_blank(template: dict, params: dict) -> tuple[dict, dict]:
    """
    Returns (frontend_payload, grading_data).
    frontend_payload contains everything the UI needs except the answer.
    grading_data contains what the grading engine needs.
    """
    frontend = {
        "question": _fill(template["question"], params),
        "answer_input": template.get("answer_input", "expression"),
        "hint": template.get("hint"),
        "placeholder": template.get("placeholder", "Răspuns..."),
    }
    grading = {
        "correct_expr": _fill(template["answer_expr"], params),
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
        "left": left,
        "right": right,
        "options": [
            {"id": "<", "text": "<"},
            {"id": "=", "text": "="},
            {"id": ">", "text": ">"},
        ],
    }
    grading = {
        "left_expr": left,
        "right_expr": right,
    }
    return frontend, grading


def _build_drag_order(template: dict, params: dict) -> tuple[dict, dict]:
    """Build drag-to-order instance."""
    items_filled = [_fill(item, params) for item in template["items"]]
    direction = template.get("order_direction", "ascending")

    # Determine correct order (numeric sort where possible)
    def sort_key(x: str):
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
    # Re-shuffle until display order differs from correct order
    # (avoid trivially pre-solved exercises)
    attempts = 0
    while display_items == correct_order and attempts < 10:
        random.shuffle(display_items)
        attempts += 1

    frontend = {
        "question": _fill(template.get("question", "Ordonați:"), params),
        "items": display_items,
        "order_direction": direction,
    }
    grading = {
        "correct_order": correct_order,
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

    return instance


def decode_instance_token(token: str) -> dict:
    """
    Decode and verify a signed instance token.

    Returns the payload dict with keys: exercise_id, exercise_type, grading_data.
    Raises signing.BadSignature if tampered or expired.
    """
    return signing.loads(token, salt=_TOKEN_SALT)
