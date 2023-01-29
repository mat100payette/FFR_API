from dataclasses import dataclass

@dataclass
class ChartArgs:
    level: int
    extended: bool

@dataclass
class AllChartArgs:
    start_id: int
    end_id: int
    compressed: bool
    extended: bool

@dataclass
class LevelScoresArgs:
    level: int
    page: int
    limit: int

@dataclass
class AllLevelScoresArgs:
    limit: int
    start_id: int
    end_id: int
    compressed: bool

@dataclass
class LevelRanksArgs:
    userid: int = 0
    username: str = ''