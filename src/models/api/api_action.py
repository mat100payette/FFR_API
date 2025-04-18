from enum import Enum


class ApiAction(Enum):
    CHART = "chart"
    ALL_CHARTS = "all_charts"
    CREDITS = "credits"
    LEVEL_RANKS = "ranks"
    SONG_LIST = "songlist"
    RECENT_GAMES = "new_recent_games"
    ACHIEVEMENTS = "achievements"
    LEVEL_SCORES = "level_scores_flip"
    ALL_LEVEL_SCORES = "all_level_scores"
    BLACK_BOX_CALC_RESULTS = "black_box_calc_results"
    VIEWER = "viewer"
