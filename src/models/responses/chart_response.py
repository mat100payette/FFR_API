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
    frame: int
    dir: int
    color: int
    ms: int

class ChartResponse(Struct):
    info: ChartInfo
    chart: list[ChartNote]