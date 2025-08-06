from datetime import datetime
from typing import Literal

from models.charts.extended_chart import ChartHit, ChartInfo, ExtendedChart


def _create_hit(ms: int, hand: int, finger: int, gap: int = 0, manip: int = 0, spread_ms: int = 0) -> ChartHit:
    return ChartHit(hand=hand, finger=finger, ms=ms, gap=gap, manip=manip, spread_ms=spread_ms)


def _generate_base_chart(hits: list[ChartHit], chart_id: int) -> ExtendedChart:
    return ExtendedChart(
        info=ChartInfo(
            id=chart_id,
            name=f"Test Chart {chart_id}",
            genre=0,
            difficulty=1,
            length="0:05",
            note_count=len(hits),
            timestamp=int(datetime.now().timestamp()),
            timestamp_format="unix",
        ),
        chart=[],  # Not relevant for axiom testing
        hits=hits,
        extended_hits=[],
        version=1,
    )


def generate_axiom1_jacklike_charts() -> list[ExtendedChart]:
    """
    Axiom 1: Monotonicity of Jack-like Transitions.

    Generates 3 charts with the same pattern of jack-like transitions (e.g., repeated same-finger or jump transitions)
    on the same hand but with increasing gap values (e.g., 50ms, 100ms, 150ms).

    The difficulty model should assign strictly decreasing difficulty as the gap increases, i.e.,
    shorter gaps are harder.

    Expected: D(g=50) > D(g=100) > D(g=150)
    """
    charts = []
    transition = [(1, 1), (2, 2)] * 5  # Same-finger reps, simulate jack-like transitions

    for i, gap in enumerate([50, 100, 150]):
        hits = []
        current_ms = 0
        for finger, next_finger in transition:
            hits.append(_create_hit(current_ms, hand=0, finger=finger, gap=gap))
            current_ms += gap
        charts.append(_generate_base_chart(hits, chart_id=100 + i))

    return charts


def generate_axiom2_alternating_charts() -> list[ExtendedChart]:
    """
    Axiom 2: Monotonicity of Alternating Singles with Gap > 100ms.

    Generates 3 charts with alternating single-finger hits on the same hand (e.g., left-right-left-right)
    where each pair is spaced with increasing gaps (e.g., 110ms, 130ms, 160ms).

    These transitions correspond to trill patterns (t=0). Difficulty should decrease as the gap increases.

    Expected: D(g=110) > D(g=130) > D(g=160)
    """
    charts = []
    transition = [(1, 2)] * 5  # Alternating singles: left and right finger

    for i, gap in enumerate([110, 130, 160]):
        hits = []
        current_ms = 0
        for f1, f2 in transition:
            hits.append(_create_hit(current_ms, hand=0, finger=f1, gap=gap))
            current_ms += gap
            hits.append(_create_hit(current_ms, hand=0, finger=f2, gap=gap))
            current_ms += gap
        charts.append(_generate_base_chart(hits, chart_id=200 + i))

    return charts


def generate_axiom3_repetition_charts(transition_type: Literal["jack", "alt", "ljump_rjump"]) -> list[ExtendedChart]:
    """
    Axiom 3: Monotonicity of Repetition.

    Generates charts with the same transition type and fixed gap (80ms), but increasing number of transitions.

    Difficulty should increase as the number of repeated transitions increases, even if the motion type and
    timing are unchanged.

    Args:
        transition_type: Type of transition pattern to simulate:
            - "jack": repeated same-finger hits (e.g., finger=1) → tests jacks (t=1)
            - "alt": alternating fingers (e.g., 1,2,1,2) → tests trills (t=0)
            - "ljump_rjump": left-single to jump → tests jack-like [2,3,2,3...] patterns

    Expected: D(n=4) < D(n=8) < D(n=12)
    """
    gap = 80
    charts = []

    if transition_type == "jack":
        finger = 1
        for i, reps in enumerate([4, 8, 12]):
            hits = []
            current_ms = 0
            for _ in range(reps):
                hits.append(_create_hit(current_ms, hand=0, finger=finger, gap=gap))
                current_ms += gap
            charts.append(_generate_base_chart(hits, chart_id=300 + i))

    elif transition_type == "alt":
        for i, reps in enumerate([4, 8, 12]):
            hits = []
            current_ms = 0
            for _ in range(reps):
                hits.append(_create_hit(current_ms, hand=0, finger=1, gap=gap))
                current_ms += gap
                hits.append(_create_hit(current_ms, hand=0, finger=2, gap=gap))
                current_ms += gap
            charts.append(_generate_base_chart(hits, chart_id=310 + i))

    elif transition_type == "ljump_rjump":
        for i, reps in enumerate([4, 8, 12]):
            hits = []
            current_ms = 0
            for _ in range(reps):
                hits.append(_create_hit(current_ms, hand=0, finger=2, gap=gap))  # right finger
                current_ms += gap
                hits.append(_create_hit(current_ms, hand=0, finger=3, gap=gap))  # jump
                current_ms += gap
            charts.append(_generate_base_chart(hits, chart_id=320 + i))

    return charts
