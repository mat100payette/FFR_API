import json

import msgspec
import requests

from models.api.api_action_args import AllChartArgs, BlackBoxCalcArgs
from models.responses.chart_response import ChartResponse
from services.ffr_api_service import get_all_charts
from utils.io import write_json_to_file

_API_URL = "https://uxswva20wb.execute-api.us-east-1.amazonaws.com/prod/autodifficulty"


def _get_data(body: dict):
    response = requests.post(
        url=_API_URL,
        json=body,
    )
    response.raise_for_status()

    if not response.ok:
        raise Exception(f"The request returned an error: {response.reason}")

    json_response = response.json()
    is_success: bool = False

    if isinstance(json_response, dict):
        api_status = json_response.get("status")
        is_success = api_status is None or api_status >= 0
    else:
        is_success = response.ok

    if not is_success:
        raise Exception(f'The api returned an error: {json_response["error"]}')

    return response.content


def get_complete_ffr_estimates(args: BlackBoxCalcArgs):
    charts_args = AllChartArgs(
        1,
        10000,
        True,
        False,
        r"C:\GitHub\FFR_API\data",
        r"C:\GitHub\FFR_API\data",
    )

    ffr_charts: list[ChartResponse | None] = get_all_charts(charts_args)

    results = []
    for ffr_chart in ffr_charts:
        if ffr_chart is None:
            continue

        response = _get_data(
            body={
                "operation": "predict_difficulty",
                "payload": json.loads(msgspec.json.encode(ffr_chart.chart).decode("utf-8")),
            }
        )

        try:
            estimated_diff = float(response.decode())
        except Exception as e:
            print(e)
            pass

        results.append(
            (
                ffr_chart.info.id,
                ffr_chart.info.name,
                ffr_chart.info.difficulty,
                estimated_diff,
            )
        )

    write_json_to_file(results, r"C:\GitHub\FFR_API\data\ffr_estimates.json")
