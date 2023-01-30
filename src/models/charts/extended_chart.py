from msgspec import Struct

class ChartInfo(Struct):
    id: int
    name: str
    genre: int
    difficulty: int
    length: str
    note_count: int
    timestamp: int
    timestamp_format: str

class ChartNote(Struct, array_like=True):
    dir: str
    frame: int
    color: str
    ms: int

class ChartHit(Struct, array_like=True):
    hand: int
    finger: int
    ms: int
    gap: int

class ExtendedChart(Struct):
    info: ChartInfo
    chart: list[ChartNote]
    hits: list[ChartHit]


def left_hand_hits(chart: ExtendedChart):
    return [hit for hit in chart.hits if hit.hand == 0]

def right_hand_hits(chart: ExtendedChart):
    return [hit for hit in chart.hits if hit.hand == 1]