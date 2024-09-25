from models.api.api_action_args import (
    AllChartArgs,
    AllLevelScoresArgs,
    ChartArgs,
    LevelScoresArgs,
    SongListArgs,
    ViewerArgs,
)
from services.api_service import (
    get_all_charts,
    get_all_level_scores,
    get_chart,
    get_level_scores,
    get_song_list,
)
from visualization.viewer import run_viewer


def run(args):
    if (isinstance(args, ViewerArgs)):
        return run_viewer(args)
    
    if (isinstance(args, SongListArgs)):
        return get_song_list(args)

    if (isinstance(args, ChartArgs)):
        return get_chart(args)

    if (isinstance(args, AllChartArgs)):
        return get_all_charts(args)

    if (isinstance(args, LevelScoresArgs)):
        return get_level_scores(args)

    if (isinstance(args, AllLevelScoresArgs)):
        return get_all_level_scores(args)
