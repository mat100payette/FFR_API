from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin

@dataclass
class ChartInfo(DataClassJsonMixin):
    id: int
    name: str
    genre: int
    difficulty: int
    length: str
    note_count: int
    timestamp: int
    timestamp_format: str

@dataclass
class ChartNote(DataClassJsonMixin):
    dir: str
    frame: int
    color: str
    ms: int

@dataclass
class ChartHit(DataClassJsonMixin):
    hand: int
    finger: int
    ms: int
    gap: int

@dataclass
class ExtendedChart(DataClassJsonMixin):
    info: ChartInfo
    chart: list[ChartNote]
    hits: list[ChartHit]


def left_hand_hits(chart: ExtendedChart):
    return [hit for hit in chart.hits if hit.hand == 0]

def right_hand_hits(chart: ExtendedChart):
    return [hit for hit in chart.hits if hit.hand == 1]