from typing import Callable, Literal

from chart_generation.axiom_based_charts import (
    generate_axiom1_jacklike_charts,
    generate_axiom2_alternating_charts,
    generate_axiom3_repetition_charts,
)

from models.charts.extended_chart import ExtendedChart


def _is_strictly_decreasing(values: list[float]) -> bool:
    return all(a > b for a, b in zip(values, values[1:]))


def _is_strictly_increasing(values: list[float]) -> bool:
    return all(a < b for a, b in zip(values, values[1:]))


def assert_axiom1(difficulty_fn: Callable[[ExtendedChart], float]) -> None:
    """
    Axiom 1: Jack-like transitions should be harder with smaller gaps.
    """
    charts = generate_axiom1_jacklike_charts()
    scores = [difficulty_fn(c) for c in charts]
    assert _is_strictly_decreasing(scores), f"Axiom 1 failed: expected decreasing difficulty with increasing gap. Scores: {scores}"


def assert_axiom2(difficulty_fn: Callable[[ExtendedChart], float]) -> None:
    """
    Axiom 2: Alternating singles (>100ms gap) should be harder when closer together.
    """
    charts = generate_axiom2_alternating_charts()
    scores = [difficulty_fn(c) for c in charts]
    assert _is_strictly_decreasing(scores), f"Axiom 2 failed: expected decreasing difficulty with increasing gap. Scores: {scores}"


def assert_axiom3(difficulty_fn: Callable[[ExtendedChart], float]) -> None:
    """
    Axiom 3: Repetition of any transition type should increase difficulty.
    """
    ttypes: list[Literal["jack", "alt", "ljump_rjump"]] = ["jack", "alt", "ljump_rjump"]
    for ttype in ttypes:
        charts = generate_axiom3_repetition_charts(ttype)
        scores = [difficulty_fn(c) for c in charts]
        assert _is_strictly_increasing(
            scores
        ), f"Axiom 3 failed for transition '{ttype}': expected increasing difficulty with repetition. Scores: {scores}"
