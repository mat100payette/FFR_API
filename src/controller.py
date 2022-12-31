from models.api_action_args import AllChartArgs, AllLevelScoresArgs, ChartArgs, LevelScoresArgs
from services.service import get_all_charts, get_all_level_scores, get_chart, get_level_scores


def call_api(args):
    if (isinstance(args, ChartArgs)):
        return get_chart(args)

    if (isinstance(args, AllChartArgs)):
        return get_all_charts(args)

    if (isinstance(args, LevelScoresArgs)):
        return get_level_scores(args)

    if (isinstance(args, AllLevelScoresArgs)):
        return get_all_level_scores(args)
