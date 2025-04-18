from msgspec import Struct

from models.responses.chart_response import ChartNote


class BlackBoxCalcChart(Struct, array_like=True):
    notes: ChartNote
