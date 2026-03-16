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
# Prevents DoS on pathological inputs like 9^9^9^9.
GRADE_TIMEOUT_SECONDS = 5


# ─── Timeout helper ───────────────────────────────────────────────────────────

class GradingTimeout(Exception):
    pass


@contextmanager
def time_limit(seconds: int):
    """Context manager that raises GradingTimeout after `seconds`."""
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

    Handles:
      - Romanian division notation:  : → /
      - Implicit multiplication:     2(3) → 2*(3)   [handled by SymPy transform]
      - Leading/trailing whitespace
    """
    s = raw.strip()
    # Replace Romanian division sign with Python division.
    # Careful: don't replace inside tokens like "10:00" — here we use word
    # boundaries, but since these are math expressions it's safe to be greedy.
    s = s.replace(":", "/")
    return s


# ─── Core graders ─────────────────────────────────────────────────────────────

def grade_expression(
    student_raw: str,
    correct_expr: str,
) -> tuple[bool, Optional[str]]:
    """
    Compare student answer to a correct expression symbolically.

    Both sides are parsed by SymPy; if their difference simplifies to 0
    they are considered equal.

    Returns:
        (is_correct, error_message)
        error_message is None when parsing succeeded (answer may still be wrong).
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

    Evaluates both sides numerically/symbolically and determines the
    correct relation, then checks against the student's choice.

    Returns:
        (is_correct, error_message)
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
    """
    Grade multiple choice — exact match on option ID.

    Returns:
        (is_correct, None)
    """
    return student_answer.strip() == correct_option_id.strip(), None


def grade_drag_order(
    student_order: list,
    correct_order: list,
) -> tuple[bool, None]:
    """
    Grade drag-to-order — compare ordered lists element-by-element.

    Returns:
        (is_correct, None)
    """
    return list(student_order) == list(correct_order), None


# ─── Dispatcher ───────────────────────────────────────────────────────────────

def grade_attempt(
    exercise_type: str,
    student_answer,
    grading_data: dict,
) -> tuple[bool, Optional[str]]:
    """
    Unified grading dispatcher.

    Args:
        exercise_type:   One of fill_blank | comparison | multiple_choice | drag_order
        student_answer:  Raw student input (string or list for drag_order)
        grading_data:    Dict produced by exercise_engine containing everything
                         needed to evaluate the answer:
                           fill_blank      → {"correct_expr": "..."}
                           comparison      → {"left_expr": "...", "right_expr": "..."}
                           multiple_choice → {"correct_option_id": "..."}
                           drag_order      → {"correct_order": [...]}

    Returns:
        (is_correct, error_message)
    """
    if exercise_type == "fill_blank":
        return grade_expression(str(student_answer), grading_data["correct_expr"])

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
