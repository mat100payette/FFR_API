import argparse
from typing import Callable

from models.api.api_action import ApiAction
from models.api.api_action_args import AllChartArgs, AllLevelScoresArgs, ChartArgs, LevelScoresArgs

def parse_args(key_setter: Callable[[str], None]):
    parser = argparse.ArgumentParser(description='Args for API experiments.')
    parser.add_argument('apikey', help='Your API key')

    # Add subparsers

    subparsers = parser.add_subparsers(dest='action', help='The params for your specific API action')

    parser_chart = subparsers.add_parser(ApiAction.CHART.value, help='Chart parameters')
    parser_chart.add_argument('-level', '--L', type=int, help='The level from which to pull chart info', default=1)
    parser_chart.add_argument('-comp', '--C', type=bool, help='Compress output file', default=False, action=argparse.BooleanOptionalAction)
    parser_chart.add_argument('-extended', '--X', type=int, help='Extended chart data', default=False, action=argparse.BooleanOptionalAction)

    parser_all_charts = subparsers.add_parser(ApiAction.ALL_CHARTS.value, help='All charts parameters')
    parser_all_charts.add_argument('-startid', '--S', type=int, help='The song id to start from', default=1)
    parser_all_charts.add_argument('-endid', '--E', type=int, help='The song id to end before', default=10000)
    parser_all_charts.add_argument('-comp', '--C', type=bool, help='Compress output files', default=False, action=argparse.BooleanOptionalAction)
    parser_all_charts.add_argument('-extended', '--X', type=int, help='Extended chart data', default=False, action=argparse.BooleanOptionalAction)

    parser_level_scores = subparsers.add_parser(ApiAction.LEVEL_SCORES.value, help='Level scores parameters')
    parser_level_scores.add_argument('-level', '--L', type=int, help='The level from which to pull scores', default=1)
    parser_level_scores.add_argument('-page', '--P', type=int, help='The page of scores to get', default=0)
    parser_level_scores.add_argument('-limit', '--M', type=int, help='The page size', default=100)

    parser_all_level_scores = subparsers.add_parser(ApiAction.ALL_LEVEL_SCORES.value, help='All level scores parameters')
    parser_all_level_scores.add_argument('-limit', '--M', type=int, help='The number of scores per level', default=100)
    parser_all_level_scores.add_argument('-startid', '--S', type=int, help='The song id to start from', default=1)
    parser_all_level_scores.add_argument('-endid', '--E', type=int, help='The song id to end before', default=10000)
    parser_all_level_scores.add_argument('-comp', '--C', type=bool, help='Compress output files', default=False, action=argparse.BooleanOptionalAction)

    parsed_args = parser.parse_args()

    # Set the API key and retrieve the action

    api_key: str = parsed_args.apikey
    key_setter(api_key)
    
    action: str = parsed_args.action

    # Create typed args object

    if (action == ApiAction.CHART.value):
        return ChartArgs(parsed_args.L, parsed_args.C, parsed_args.X)

    if (action == ApiAction.ALL_CHARTS.value):
        return AllChartArgs(parsed_args.S, parsed_args.E, parsed_args.C, parsed_args.X)

    if (action == ApiAction.LEVEL_SCORES.value):
        return LevelScoresArgs(parsed_args.L, parsed_args.P, parsed_args.M)

    if (action == ApiAction.ALL_LEVEL_SCORES.value):
        return AllLevelScoresArgs(parsed_args.M, parsed_args.S, parsed_args.E, parsed_args.C)

    raise Exception(f'Unsupported api action "{action}"')
    