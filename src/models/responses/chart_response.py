from dataclasses import dataclass
from typing import Union
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
    dir: int
    frame: int
    color: int
    ms: int

@dataclass
class ChartResponse(DataClassJsonMixin):
    info: ChartInfo
    chart: list[ChartNote]


def parse_chart_notes(raw_notes: list[list[Union[str, int]]]):
    return list(map(lambda raw_note: ChartNote(*raw_note), raw_notes))