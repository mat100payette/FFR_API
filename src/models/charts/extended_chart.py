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
    hand: int
    finger: int
    ms: int
    gap: int
    manip: int
    spread_ms: int


class ExtendedChart(Struct):
    info: ChartInfo
    chart: list[ChartNote]
    hits: list[ChartHit]
    version: int


def left_hand_hits(chart: ExtendedChart):
    return [hit for hit in chart.hits if hit.hand == 0]


def right_hand_hits(chart: ExtendedChart):
    return [hit for hit in chart.hits if hit.hand == 1]
