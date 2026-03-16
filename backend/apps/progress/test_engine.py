"""
Test session engine for MathEd Romania.

Builds a concrete test session from a Test's composition config,
pulling exercises by category and difficulty from the lesson(s)
associated with the test.
"""
import random
from apps.content.models import Exercise
from apps.progress.exercise_engine import generate_instance


def build_test_session(test) -> list[dict]:
    """
    Given a Test instance, generate a list of exercise instances
    according to the test's composition.

    Composition format:
    [
      {"category": "expanded_form", "count": 2, "difficulty": "easy", "weight": 25},
      {"category": "digit_identification", "count": 3, "difficulty": "medium", "weight": 50},
      ...
    ]

    If category is "" or omitted, any category is accepted.
    If difficulty is omitted, any difficulty is accepted.

    Returns a list of instance dicts (same format as practice endpoint),
    each augmented with a "weight" key for scoring.
    """
    # Collect the pool of eligible exercises
    if test.scope == "lesson" and test.lesson:
        base_qs = Exercise.objects.filter(
            lesson=test.lesson,
            is_active=True,
        )
    elif test.scope == "unit" and test.unit:
        base_qs = Exercise.objects.filter(
            lesson__unit=test.unit,
            is_active=True,
        )
    else:
        return []

    instances = []

    for slot in test.composition:
        category = slot.get("category", "")
        difficulty = slot.get("difficulty", "")
        count = slot.get("count", 1)
        weight = slot.get("weight", 10)

        qs = base_qs
        if category:
            qs = qs.filter(category=category)
        if difficulty:
            qs = qs.filter(difficulty=difficulty)

        exercises = list(qs)
        if not exercises:
            # Fall back to any exercise from the pool for this slot
            exercises = list(base_qs)
        if not exercises:
            continue

        # Sample with replacement if fewer available than needed
        selected = (
            random.sample(exercises, min(count, len(exercises)))
            if len(exercises) >= count
            else random.choices(exercises, k=count)
        )

        for exercise in selected:
            try:
                instance = generate_instance(exercise)
                instance["weight"] = weight
                instances.append(instance)
            except Exception:
                continue

    random.shuffle(instances)
    return instances


def calculate_score(composition: list, answers: dict) -> tuple[float, bool]:
    """
    Calculate the final score from submitted answers.

    answers format: {"0": {"is_correct": True}, "1": {"is_correct": False}, ...}

    Returns (score_percent, passed) based on weighted composition.
    Each slot's weight is taken from the stored instance's "weight" field.
    """
    if not answers:
        return 0.0, False

    total_weight = sum(
        inst_data.get("weight", 10)
        for inst_data in answers.values()
    )
    if total_weight == 0:
        return 0.0, False

    earned_weight = sum(
        inst_data.get("weight", 10)
        for inst_data in answers.values()
        if inst_data.get("is_correct")
    )

    score = round((earned_weight / total_weight) * 100, 2)
    return score, False  # pass_threshold checked by caller