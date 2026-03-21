"""
Grading engine for MathEd Romania.

Uses SymPy for symbolic math comparison so any equivalent expression
is accepted as correct — student can write 2^40, 2^(19+21), or
1099511627776 and all grade as correct for 2^19 * 2^21.

Romanian math notation supported:
  - ^ for exponentiation  (converted to **)
  - : for division        (converted to /)
"""
import re
import signal
from contextlib import contextmanager
from typing import Optional

import sympy
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

# ─── SymPy parser config ──────────────────────────────────────────────────────

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,  # ^ → **
)

# Maximum time (seconds) allowed for a single SymPy simplification.
GRADE_TIMEOUT_SECONDS = 5


# ─── Timeout helper ───────────────────────────────────────────────────────────

class GradingTimeout(Exception):
    pass


@contextmanager
def time_limit(seconds: int):
    """Context manager that raises GradingTimeout after `seconds`.
    No-op on Windows where SIGALRM is unavailable.
    """
    if not hasattr(signal, "SIGALRM"):
        # Windows — no SIGALRM support, skip timeout
        yield
        return

    def _handler(signum, frame):
        raise GradingTimeout("Grading timed out")

    old = signal.signal(signal.SIGALRM, _handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


# ─── Input normalization ──────────────────────────────────────────────────────

def normalize(raw: str) -> str:
    """
    Normalize student input to a form SymPy can parse.
    """
    s = raw.strip()
    s = s.replace(":", "/")
    return s


# ─── Core graders ─────────────────────────────────────────────────────────────

def grade_expression(
    student_raw: str,
    correct_expr: str,
) -> tuple[bool, Optional[str]]:
    """
    Compare student answer to a correct expression symbolically.
    """
    if not student_raw or not student_raw.strip():
        return False, "empty_input"

    try:
        student_norm = normalize(student_raw)
        correct_norm = normalize(correct_expr)

        student_sym = parse_expr(student_norm, transformations=TRANSFORMATIONS)
        correct_sym = parse_expr(correct_norm, transformations=TRANSFORMATIONS)

        with time_limit(GRADE_TIMEOUT_SECONDS):
            diff = sympy.simplify(student_sym - correct_sym)
            is_correct = diff == sympy.Integer(0)

        return is_correct, None

    except GradingTimeout:
        return False, "timeout"
    except Exception as exc:  # noqa: BLE001
        return False, f"parse_error: {exc}"


def grade_comparison(
    student_answer: str,
    left_expr: str,
    right_expr: str,
) -> tuple[bool, Optional[str]]:
    """
    Grade a comparison exercise where the student selects <, =, or >.
    """
    try:
        left_sym = parse_expr(normalize(left_expr), transformations=TRANSFORMATIONS)
        right_sym = parse_expr(normalize(right_expr), transformations=TRANSFORMATIONS)

        with time_limit(GRADE_TIMEOUT_SECONDS):
            diff = sympy.simplify(left_sym - right_sym)

        if diff == sympy.Integer(0):
            correct = "="
        elif diff > 0:
            correct = ">"
        else:
            correct = "<"

        return student_answer.strip() == correct, None

    except GradingTimeout:
        return False, "timeout"
    except Exception as exc:  # noqa: BLE001
        return False, f"parse_error: {exc}"


def grade_multiple_choice(
    student_answer: str,
    correct_option_id: str,
) -> tuple[bool, None]:
    """Grade multiple choice — exact match on option ID."""
    return student_answer.strip() == correct_option_id.strip(), None


def grade_drag_order(
    student_order: list,
    correct_order: list,
) -> tuple[bool, None]:
    """Grade drag-to-order — compare ordered lists element-by-element."""
    return list(student_order) == list(correct_order), None


def grade_multi_fill_blank(
    student_answers: dict,
    correct_map: dict,
) -> tuple[bool, Optional[str]]:
    """
    Grade multi-field fill-in-the-blank.

    student_answers: {"a": "3", "b": "7", "c": "0", "d": "9"}
    correct_map:     {"a": "3", "b": "7", "c": "0", "d": "9"}

    All fields must be correct (symbolic match via grade_expression).
    Returns is_correct=False on the first wrong field found.
    """
    if not isinstance(student_answers, dict):
        return False, "invalid_format"

    for key, correct_expr in correct_map.items():
        student_val = str(student_answers.get(key, "")).strip()
        is_correct, error = grade_expression(student_val, correct_expr)
        if not is_correct:
            return False, error

    return True, None


# ─── Dispatcher ───────────────────────────────────────────────────────────────

def grade_attempt(
    exercise_type: str,
    student_answer,
    grading_data: dict,
) -> tuple[bool, Optional[str]]:
    """
    Unified grading dispatcher.

    Args:
        exercise_type:   fill_blank | multi_fill_blank | comparison |
                         multiple_choice | drag_order
        student_answer:  string, list (drag_order), or dict (multi_fill_blank)
        grading_data:    dict from exercise_engine with grading keys
    """
    if exercise_type == "fill_blank":
        # Set-membership grading
        if "valid_set" in grading_data:
            try:
                student_int = int(str(student_answer).strip())
                return student_int in grading_data["valid_set"], None
            except (ValueError, TypeError):
                return False, "invalid_format"
        # Standard symbolic grading
        return grade_expression(str(student_answer), grading_data["correct_expr"])

    elif exercise_type == "multi_fill_blank":
        return grade_multi_fill_blank(
            student_answer,
            grading_data["correct_map"],
        )

    elif exercise_type == "comparison":
        return grade_comparison(
            str(student_answer),
            grading_data["left_expr"],
            grading_data["right_expr"],
        )

    elif exercise_type == "multiple_choice":
        return grade_multiple_choice(
            str(student_answer),
            grading_data["correct_option_id"],
        )

    elif exercise_type == "drag_order":
        return grade_drag_order(
            student_answer,
            grading_data["correct_order"],
        )

    return False, f"unknown_exercise_type: {exercise_type}"
