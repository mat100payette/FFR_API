from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin

@dataclass
class LevelScoresSong(DataClassJsonMixin):
    id: int
    songname: str
    note_count: int
    time: str
    difficulty: int
    players: int

@dataclass
class LevelScoresScore(DataClassJsonMixin):
    id: int
    username: str
    perfect: int
    good: int
    average: int
    miss: int
    boo: int
    timestamp: int
    raw_score: int
    user_level: float
    rank: int
    aaaeq: float

@dataclass
class LevelScoresResponse(DataClassJsonMixin):
    song: LevelScoresSong
    scores: list[LevelScoresScore]