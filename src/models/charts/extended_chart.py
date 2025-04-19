from msgspec import Struct

from models.responses.chart_response import ChartNote


class ChartInfo(Struct):
    id: int
    name: str
    genre: int
    difficulty: int
    length: str
    note_count: int
    timestamp: int
    timestamp_format: str


class ChartHit(Struct, array_like=True):
    hand: int  # 0 or 1 for left or right hand.
    finger: int  # 1 or 2 for left and right finger on that hand, 3 for jump.
    ms: int  # ms timing of the hit.
    gap: int  # ms between this and previous hit on same hand. Defaults to `ms` for the first hit on each hand.
    manip: int  # 0-100 score of how plausible this hit is to manip as a jump with the following hit on the same hand.
    spread_ms: int  # ms adjusted to a spread out chart that minimizes effort and maximizes precision.


class ManipCorrectedHit(Struct, array_like=True):
    hand: int
    finger: int
    ms: int
    gap: int
    precision: int  # The ms timing allowed for a perfect on that hit


class ManipCorrectedHitWithTransition(Struct, array_like=True):
    hand: int
    finger: int
    ms: int
    gap: int
    precision: int  # The ms timing allowed for a perfect on that hit
    transition: int  # Discrete variable representing the transition type with the following hit on the same hand


class ExtendedChart(Struct):
    info: ChartInfo
    chart: list[ChartNote]
    hits: list[ChartHit]
    extended_hits: list[ManipCorrectedHitWithTransition]
    version: int


TRANSITION_LABELS = {
    0: "trill",
    1: "jack",
    2: "jump_to_single",
    3: "single_to_jump",
    4: "jumpstream",
}


def left_hand_hits(chart: ExtendedChart):
    return [hit for hit in chart.hits if hit.hand == 0]


def right_hand_hits(chart: ExtendedChart):
    return [hit for hit in chart.hits if hit.hand == 1]
