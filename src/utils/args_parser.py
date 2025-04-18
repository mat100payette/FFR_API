import argparse
from typing import Callable

from models.api.api_action import ApiAction
from models.api.api_action_args import (
    AllChartArgs,
    AllLevelScoresArgs,
    BlackBoxCalcArgs,
    ChartArgs,
    LevelScoresArgs,
    SongListArgs,
    ViewerArgs,
)


def parse_args(key_setter: Callable[[str], None]):
    parser = argparse.ArgumentParser(description="Args for API experiments.")
    parser.add_argument("apikey", type=str, nargs=argparse.OPTIONAL, help="Your API key", default=None)

    # Add subparsers

    subparsers = parser.add_subparsers(dest="action", help="The params for your specific API action")

    subparsers.add_parser(ApiAction.VIEWER.value, help="Interactive GUI")

    parser_chart = subparsers.add_parser(ApiAction.CHART.value, help="Chart parameters")
    parser_chart.add_argument("-level", "--L", type=int, help="The level from which to pull chart info", default=1)
    parser_chart.add_argument("-comp", "--C", type=bool, help="Compress output file", default=False, action=argparse.BooleanOptionalAction)
    parser_chart.add_argument("-extended", "--X", type=bool, help="Extended chart data", default=False, action=argparse.BooleanOptionalAction)

    parser_chart_group = parser_chart.add_mutually_exclusive_group()
    parser_chart_group.add_argument("-todir", "--T", type=str, help="Directory to save the data to", nargs=argparse.OPTIONAL)
    parser_chart_group.add_argument("-fromfile", "--F", type=str, help="File to load the data from", nargs=argparse.OPTIONAL)

    parser_all_charts = subparsers.add_parser(ApiAction.ALL_CHARTS.value, help="All charts parameters")
    parser_all_charts.add_argument("-startid", "--S", type=int, help="The song id to start from", default=1)
    parser_all_charts.add_argument("-endid", "--E", type=int, help="The song id to end before", default=10000)
    parser_all_charts.add_argument("-comp", "--C", type=bool, help="Compress output files", default=False, action=argparse.BooleanOptionalAction)
    parser_all_charts.add_argument("-extended", "--X", type=bool, help="Extended chart data", default=False, action=argparse.BooleanOptionalAction)

    parser_all_charts_group = parser_all_charts.add_mutually_exclusive_group()
    parser_all_charts_group.add_argument("-todir", "--T", type=str, help="Directory to save the data to", nargs=argparse.OPTIONAL)
    parser_all_charts_group.add_argument("-fromdir", "--F", type=str, help="Directory to load the data from", nargs=argparse.OPTIONAL)

    parser_level_scores = subparsers.add_parser(ApiAction.LEVEL_SCORES.value, help="Level scores parameters")
    parser_level_scores.add_argument("-level", "--L", type=int, help="The level from which to pull scores", default=1)
    parser_level_scores.add_argument("-page", "--P", type=int, help="The page of scores to get", default=0)
    parser_level_scores.add_argument("-limit", "--M", type=int, help="The page size", default=100)

    subparsers.add_parser(ApiAction.SONG_LIST.value, help="Song list")

    parser_all_level_scores = subparsers.add_parser(ApiAction.ALL_LEVEL_SCORES.value, help="All level scores parameters")
    parser_all_level_scores.add_argument("-limit", "--M", type=int, help="The number of scores per level", default=100)
    parser_all_level_scores.add_argument("-startid", "--S", type=int, help="The song id to start from", default=1)
    parser_all_level_scores.add_argument("-endid", "--E", type=int, help="The song id to end before", default=10000)
    parser_all_level_scores.add_argument(
        "-comp", "--C", type=bool, help="Compress output files", default=False, action=argparse.BooleanOptionalAction
    )

    _parser_black_box_calc = subparsers.add_parser(ApiAction.BLACK_BOX_CALC_RESULTS.value, help="All level estimated diff from black box calc")

    parsed_args = parser.parse_args()

    # Set the API key and retrieve the action

    api_key: str = parsed_args.apikey
    key_setter(api_key)

    action: str = parsed_args.action

    if action != ApiAction.VIEWER.value and not api_key:
        raise ValueError(f"API key is required for the {action} action.")

    # Create typed args object

    match action:
        case ApiAction.VIEWER.value:
            return ViewerArgs()

        case ApiAction.SONG_LIST.value:
            return SongListArgs()

        case ApiAction.CHART.value:
            return ChartArgs(
                level=parsed_args.L,
                compressed=parsed_args.C,
                extended=parsed_args.X,
                to_dir=parsed_args.T,
                from_file=parsed_args.F,
            )

        case ApiAction.ALL_CHARTS.value:
            return AllChartArgs(
                parsed_args.S,
                parsed_args.E,
                compressed=parsed_args.C,
                extended=parsed_args.X,
                to_dir=parsed_args.T,
                from_file=parsed_args.F,
            )

        case ApiAction.LEVEL_SCORES.value:
            return LevelScoresArgs(
                parsed_args.L,
                parsed_args.P,
                parsed_args.M,
            )

        case ApiAction.ALL_LEVEL_SCORES.value:
            return AllLevelScoresArgs(
                parsed_args.M,
                parsed_args.S,
                parsed_args.E,
                parsed_args.C,
            )

        case ApiAction.BLACK_BOX_CALC_RESULTS.value:
            return BlackBoxCalcArgs()

        case _:
            raise Exception(f'Unsupported api action "{action}"')
