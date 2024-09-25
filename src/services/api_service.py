import itertools
import multiprocessing as mp

import requests
from msgspec.json import decode, encode

from models.api.api_action import ApiAction
from models.api.api_action_args import (
    AllChartArgs,
    AllLevelScoresArgs,
    ChartArgs,
    LevelRanksArgs,
    LevelScoresArgs,
    SongListArgs,
)
from models.charts.extended_chart import ExtendedChart
from models.responses.chart_response import ChartResponse
from models.responses.level_ranks_response import LevelRanksResponse
from models.responses.level_scores_response import LevelScoresResponse, LevelScoresScore
from transformers.ffr_chart_to_extended_chart import extend_ffr_chart
from utils.api import api_key, api_url, set_api_key
from utils.io import (
    build_chart_filename,
    load_compressed_json_from_file,
    load_json_from_file,
    write_compressed_json_to_file,
    write_json_to_file,
)

_DEFAULT_USERNAME = 'Zageron'


def _get_data(action: str, query_params: str | None):
    query_params_part = f'&{query_params}' if query_params else ''
    response = requests.get(f'{api_url()}?key={api_key()}&action={action}{query_params_part}')
    response.raise_for_status()

    if not response.ok:
        raise Exception(f'The request returned an error: {response.reason}')

    json_response: dict = response.json()
    api_status = json_response.get('status')

    if (api_status is not None and api_status < 0):
        raise Exception(f'The api returned an error: {json_response["error"]}')

    return response.content


def get_song_list(args: SongListArgs):
    response = _get_data(ApiAction.SONG_LIST.value)
    pass


def get_chart(args: ChartArgs):
    level_id = args.level
    query_params = f'level={level_id}'
    
    path: str | None = None
    chart: ChartResponse | ExtendedChart = None
    
    try:
        # Determine filename if from_dir or to_dir is provided
        if args.from_file:
            path = args.from_file
        elif args.to_dir:
            path = build_chart_filename(args.to_dir, args.extended, args.compressed, level_id)
        
        # Load from disk and extend if necessary
        if args.from_file:
            loaded_chart = load_compressed_json_from_file(path) if args.compressed else load_json_from_file(path)
            
            chart = decode(loaded_chart, type=ExtendedChart) if args.extended else decode(loaded_chart, type=ChartResponse)
        
        # Fetch from API and extend if necessary
        else:
            response = _get_data(ApiAction.CHART.value, query_params)
            chart = decode(response, type=ChartResponse)
            chart = extend_ffr_chart(chart) if args.extended else chart
        
        # Write to file if to_dir is specified
        if args.to_dir and not args.from_file:
            dict_data = decode(encode(chart))
            write_compressed_json_to_file(dict_data, path) if args.compressed else write_json_to_file(dict_data, path)
    
        return chart
    
    except Exception as e:
        print(f'Error on song {level_id}: {e}')


def get_all_charts(args: AllChartArgs):
    level_ids = _get_level_ids()
    ranged_level_ids = set(filter(lambda lvl_id: args.start_id <= lvl_id < args.end_id, level_ids))

    pool = mp.Pool(initializer=set_api_key, initargs=(api_key(),))
    pool.starmap(_get_all_charts_internal, zip(ranged_level_ids, itertools.repeat(args.compressed), itertools.repeat(args.extended)))


def get_level_ranks(args: LevelRanksArgs):
    if args.userid > 0:
        query_params = f'userid={args.userid}'
    else:
        query_params = f'username={args.username}'

    response = _get_data(ApiAction.LEVEL_RANKS.value, query_params)
    return decode(response, type=LevelRanksResponse)


def get_level_scores(args: LevelScoresArgs):
    query_params = f'level={args.level}&page={args.page}&limit={args.limit}'

    return _get_data(ApiAction.LEVEL_SCORES.value, query_params)


def get_all_level_scores(args: AllLevelScoresArgs):
    limit = args.limit
    _has_limit = limit > 0

    level_ids = _get_level_ids()
    ranged_level_ids = set(filter(lambda lvl_id: args.start_id <= lvl_id < args.end_id, level_ids))

    pool = mp.Pool(initializer=set_api_key, initargs=(api_key(),))
    pool.starmap(_get_all_level_scores_internal, zip(ranged_level_ids, itertools.repeat(args.compressed)))


def _get_level_ids():
    default_level_ranks = get_level_ranks(LevelRanksArgs(0, _DEFAULT_USERNAME))
    return set(default_level_ranks.songs.keys())


def _get_all_level_scores_internal(level_id: int, compressed: bool):
    page_count = 0

    def parse_page(page: int):
        query_params = f'level={level_id}&page={page}'
        response = _get_data(ApiAction.LEVEL_SCORES.value, query_params)
        return decode(response, type=LevelScoresResponse)

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
        dict_data = decode(encode(complete_level_scores))

        if compressed:
            write_compressed_json_to_file(dict_data, filename)
        else:
            write_json_to_file(dict_data, filename)

    except Exception as e:
        print(f'Error on song {level_id}: {e}')


def _get_all_charts_internal(level_id: int, compressed: bool, extended: bool):
    try:
        get_chart(ChartArgs(level_id, compressed, extended))

    except Exception as e:
        print(f'Error on song {level_id}: {e}')