import numpy as np

from models.charts.extended_chart import ChartHit, ExtendedChart


def compute_difficulty(chart: ExtendedChart):
    pass


def compute_peak_window_strain_vectorized(hits: list[ChartHit], window_ms: int = 10000) -> float:
    if len(hits) < 2:
        return 0.0

    # Extract ms, gap, and manip into NumPy arrays
    ms = np.array([hit.ms for hit in hits])
    gap = np.array([hit.gap for hit in hits])
    manip = np.array([hit.manip for hit in hits])

    # Compute base strain with manip scaling (skip invalid gaps)
    valid = gap > 0
    strain = np.zeros_like(gap, dtype=np.float32)
    strain[valid] = (1.0 / gap[valid]) * (1.0 - 0.4 * manip[valid] / 100)

    # Use a sliding window approach
    peak = 0.0
    start = 0
    for end in range(len(hits)):
        # Slide window to ensure ms[end] - ms[start] <= window_ms
        while ms[end] - ms[start] > window_ms:
            start += 1
        # Sum strain within the window [start:end)
        window_strain = strain[start:end].sum()
        peak = max(peak, window_strain)

    return float(peak)
