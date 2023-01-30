from msgspec import Struct

class LevelScoresSong(Struct):
    id: int
    songname: str
    note_count: int
    time: str
    difficulty: int
    players: int

class LevelScoresScore(Struct):
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

class LevelScoresResponse(Struct):
    song: LevelScoresSong
    scores: list[LevelScoresScore]