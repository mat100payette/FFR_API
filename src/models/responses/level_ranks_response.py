from msgspec import Struct


class LevelRanksUser(Struct):
    name: str
    id: str


class LevelRanksSongInfo(Struct):
    level: int
    genre: int
    name: str
    difficulty: int
    notes: int
    length: str


class LevelRanksSongScores(Struct):
    score: int
    perfect: int
    good: int
    average: int
    miss: int
    boo: int
    combo: int
    played: int
    timestamp: int
    rank: int


class LevelRanksSong(Struct):
    info: LevelRanksSongInfo


class LevelRanksResponse(Struct):
    user: LevelRanksUser
    songs: dict[int, LevelRanksSong]
