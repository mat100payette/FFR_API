import itertools
from cache_to_disk import cache_to_disk
import multiprocessing as mp
import requests

from models.api_action import ApiAction
from models.api_action_args import AllChartArgs, AllLevelScoresArgs, ChartArgs, LevelRanksArgs, LevelScoresArgs
from models.responses.chart_response import ChartResponse, parse_chart_notes
from models.responses.level_ranks_response import LevelRanksResponse
from models.responses.level_scores_response import LevelScoresResponse, LevelScoresScore
from utils.io import write_compressed_json_to_file, write_json_to_file

_API_URL = 'https://www.flashflashrevolution.com/api/api.php'
_API_KEY = ''

_DEFAULT_USERNAME = 'Zageron'

def set_api_key(key: str):
    global _API_KEY
    _API_KEY = key

@cache_to_disk()
def _get_data(action: str, query_params: str):
    response = requests.get(f'{_API_URL}?key={_API_KEY}&action={action}&{query_params}')
    response.raise_for_status()

    if not response.ok:
        raise Exception(f'The request returned an error: {response.reason}')

    json_response: dict = response.json()
    api_status = json_response.get('status')

    if (api_status is not None and api_status < 0):
        raise Exception(f'The api returned an error: {json_response["error"]}')

    return json_response

def get_chart(args: ChartArgs):
    query_params = f'level={args.level}'

    response = _get_data(ApiAction.CHART.value, query_params)
    response['chart'] = parse_chart_notes(response['chart'])
    return ChartResponse.from_dict(response)

def get_all_charts(args: AllChartArgs):
    level_ids = _get_level_ids()
    ranged_level_ids = set(filter(lambda lvl_id: args.start_id <= lvl_id < args.end_id, level_ids))

    pool = mp.Pool(initializer=set_api_key, initargs=(_API_KEY,))
    pool.starmap(_get_complete_charts, zip(ranged_level_ids, itertools.repeat(args.compressed)))

def get_level_ranks(args: LevelRanksArgs):
    if args.userid > 0:
        query_params = f'userid={args.userid}'
    else:
        query_params = f'username={args.username}'

    response = _get_data(ApiAction.LEVEL_RANKS.value, query_params)
    return LevelRanksResponse.from_dict(response)

def get_level_scores(args: LevelScoresArgs):
    query_params = f'level={args.level}&page={args.page}&limit={args.limit}'

    return _get_data(ApiAction.LEVEL_SCORES.value, query_params)

def get_all_level_scores(args: AllLevelScoresArgs):
    limit = args.limit
    has_limit = limit > 0

    level_ids = _get_level_ids()
    ranged_level_ids = set(filter(lambda lvl_id: args.start_id <= lvl_id < args.end_id, level_ids))

    pool = mp.Pool(initializer=set_api_key, initargs=(_API_KEY,))
    pool.starmap(_get_complete_level_scores, zip(ranged_level_ids, itertools.repeat(args.compressed)))

def _get_level_ids():
    default_level_ranks = get_level_ranks(LevelRanksArgs(0, _DEFAULT_USERNAME))
    return set(default_level_ranks.songs.keys())

def _get_complete_level_scores(level_id: int, compressed: bool):
    page_count = 0

    def parse_page(page: int):
        query_params = f'level={level_id}&page={page}'
        response = _get_data(ApiAction.LEVEL_SCORES.value, query_params)
        return LevelScoresResponse.from_dict(response)

    try:
        parsed_page = parse_page(page_count)
        song_info = parsed_page.song
        song_scores: list[LevelScoresScore] = []

        while len(parsed_page.scores) > 0:
            song_scores.extend(parsed_page.scores)

            page_count += 1
            parsed_page = parse_page(page_count)
        
        complete_level_scores = LevelScoresResponse(song_info, song_scores)
        filename = f'data/level_scores/scores_{song_info.id}'
        dict_data = complete_level_scores.to_dict()

        if compressed:
            write_compressed_json_to_file(dict_data, filename)
        else:
            write_json_to_file(dict_data, filename)

    except Exception as e:
        print(f'Error on song {level_id}: {e}')

def _get_complete_charts(level_id: int, compressed: bool):
    try:
        chart = get_chart(ChartArgs(level_id))
        filename = f'data/charts/chart_{level_id}'
        dict_data = chart.to_dict()

        if compressed:
            write_compressed_json_to_file(dict_data, filename)
        else:
            write_json_to_file(dict_data, filename)

    except Exception as e:
        print(f'Error on song {level_id}: {e}')