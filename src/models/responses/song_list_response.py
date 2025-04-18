from msgspec import Struct


class SongInfo(Struct):
    id: int
    name: str
    author: str
    stepauthor: str
    genre: int
    difficulty: int
    length: str
    note_count: int
    min_nps: int
    max_nps: int
    timestamp: int
    timestamp_format: str
    swf_version: int


class SongListResponse(Struct):
    songs: list[SongInfo]
