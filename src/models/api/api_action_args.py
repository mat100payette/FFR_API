from msgspec import Struct


class ViewerArgs(Struct):
    pass

class SongListArgs(Struct):
    pass

class ChartArgs(Struct):
    level: int
    compressed: bool
    extended: bool
    to_dir: str = ''
    from_file: str = ''

class AllChartArgs(Struct):
    start_id: int
    end_id: int
    compressed: bool
    extended: bool

class LevelScoresArgs(Struct):
    level: int
    page: int
    limit: int

class AllLevelScoresArgs(Struct):
    limit: int
    start_id: int
    end_id: int
    compressed: bool

class LevelRanksArgs(Struct):
    userid: int = 0
    username: str = ''