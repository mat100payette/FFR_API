from verify_func_against_axioms import assert_axiom1, assert_axiom2, assert_axiom3

from models.charts.extended_chart import ExtendedChart


# Replace this with your real difficulty function
def dummy_difficulty_fn(chart: ExtendedChart) -> float:
    return sum(1 / hit.gap for hit in chart.hits) / len(chart.hits) + len(chart.hits) * 0.1


def test_axiom1():
    assert_axiom1(dummy_difficulty_fn)


def test_axiom2():
    assert_axiom2(dummy_difficulty_fn)


def test_axiom3():
    assert_axiom3(dummy_difficulty_fn)
