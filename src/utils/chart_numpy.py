import numpy as np

from models.charts.extended_chart import (
    ChartHit,
    ExtendedChart,
    left_hand_hits,
    right_hand_hits,
)


def _hand_data_from_hits(hits: list[ChartHit]):
    # Extract ms, finger (columns), and manip score for the given hand hits
    ms_values = np.array([hit.ms for hit in hits], dtype=np.int32)
    hand_columns = np.array([hit.finger for hit in hits], dtype=np.int8)
    manip_scores = np.array([hit.manip for hit in hits], dtype=np.int8)
    
    # Stack them together as a 2D array: each row [ms, column, manip_score]
    return np.column_stack((ms_values, hand_columns, manip_scores))

def get_left_right_hits_data(chart: ExtendedChart):
    # Get hits for each hand
    left_hits = left_hand_hits(chart)
    right_hits = right_hand_hits(chart)

    # Convert the hits into the arrow data format for both hands
    left_hits_data = _hand_data_from_hits(left_hits)
    right_hits_data = _hand_data_from_hits(right_hits)

    return left_hits_data, right_hits_data
