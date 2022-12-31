from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin

@dataclass
class LevelRanksUser(DataClassJsonMixin):
    name: str
    id: str

@dataclass
class LevelRanksSongInfo(DataClassJsonMixin):
    level: int
    genre: str
    name: str
    difficulty: int
    notes: int
    length: str

@dataclass
class LevelRanksSongScores(DataClassJsonMixin):
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

@dataclass
class LevelRanksSong(DataClassJsonMixin):
    info: LevelRanksSongInfo

@dataclass
class LevelRanksResponse(DataClassJsonMixin):
    user: LevelRanksUser
    songs: dict[int, LevelRanksSong]