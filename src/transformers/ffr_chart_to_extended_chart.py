import numpy as np
import pandas as pd
from numpy.typing import NDArray

from models.charts.extended_chart import ChartHit, ChartInfo, ExtendedChart, ManipCorrectedHit, ManipCorrectedHitWithTransition
from models.responses.chart_response import ChartNote, ChartResponse
from utils.versioning import EXTENDED_CHART_VERSION


def extend_ffr_chart(ffr_chart: ChartResponse):
    hits = compute_hits(ffr_chart)
    manip_corrected_hits = compute_manip_corrected_hits(hits)
    manip_corr_hits_with_transition = compute_hit_transitions(manip_corrected_hits)

    chart_info = ChartInfo(
        id=ffr_chart.info.id,
        name=ffr_chart.info.name,
        genre=ffr_chart.info.genre,
        difficulty=ffr_chart.info.difficulty,
        length=ffr_chart.info.length,
        note_count=len(ffr_chart.chart),
        timestamp=ffr_chart.info.timestamp,
        timestamp_format=ffr_chart.info.timestamp_format,
    )

    return ExtendedChart(chart_info, ffr_chart.chart, hits, manip_corr_hits_with_transition, EXTENDED_CHART_VERSION)


def ffr_note_dir(note: ChartNote):
    return note.dir


def ffr_note_ms(note: ChartNote):
    return note.ms


def ffr_note_hand(note: ChartNote):
    return 0 if ffr_note_dir(note) <= 1 else 1


def ffr_note_finger(note: ChartNote):
    return ffr_note_dir(note) % 2


def classify_transition_code(prev: ManipCorrectedHit, curr: ManipCorrectedHit) -> int:
    if prev.finger != 3 and curr.finger != 3:
        return 0 if prev.finger != curr.finger else 1
    elif prev.finger == 3 and curr.finger != 3:
        return 2
    elif prev.finger != 3 and curr.finger == 3:
        return 3
    elif prev.finger == 3 and curr.finger == 3:
        return 4
    return -1  # unknown


def compute_hits(ffr_chart: ChartResponse):
    np_notes = np.array(
        [
            [
                ffr_note_ms(note),
                ffr_note_hand(note),
                ffr_note_dir(note),
                ffr_note_finger(note) + 1,
            ]
            for note in ffr_chart.chart
        ],
        dtype=np.int32,
    )

    pd_notes = pd.DataFrame(np_notes)

    # Split notes into left and right hand
    notes_by_hand = pd_notes.groupby(1, as_index=False)
    notes_left_hand = pd.DataFrame(np_notes[notes_by_hand.groups[0].to_numpy()])
    notes_right_hand = pd.DataFrame(np_notes[notes_by_hand.groups[1].to_numpy()])

    # Transform notes into hits on each hand
    left_hits = notes_left_hand.groupby(0).sum().reset_index().to_numpy()[:, [0, 3]]
    right_hits = notes_right_hand.groupby(0).sum().reset_index().to_numpy()[:, [0, 3]]

    # Get the manip score of each hit
    left_hits_with_manip = get_manip_jumps_on_hand(left_hits)
    right_hits_with_manip = get_manip_jumps_on_hand(right_hits)

    spread_left_hits = iterative_smoothing_projection(left_hits[:, 0])
    spread_right_hits = iterative_smoothing_projection(right_hits[:, 0])

    # Append the data to get the correct format for ChartHit's
    extended_left_hits = np.c_[
        np.zeros(left_hits.shape[0], dtype=int).T,
        left_hits,
        np.diff(left_hits, axis=0, prepend=[[0, 0]])[:, 0],
        left_hits_with_manip[:, 2],
        spread_left_hits,
    ]
    extended_right_hits = np.c_[
        np.ones(right_hits.shape[0], dtype=int).T,
        right_hits,
        np.diff(right_hits, axis=0, prepend=[[0, 0]])[:, 0],
        right_hits_with_manip[:, 2],
        spread_right_hits,
    ]

    # Concat both hands sorted by time
    all_hits = np.concatenate((extended_left_hits, extended_right_hits), axis=0)
    all_hits_sorted_time = all_hits[all_hits[:, 1].argsort()]

    return [
        ChartHit(int(hand), int(finger), int(ms), int(gap), int(manip_score), int(spread_ms))
        for (hand, ms, finger, gap, manip_score, spread_ms) in all_hits_sorted_time
    ]


def iterative_smoothing_projection(x: NDArray[np.int32], T: int = 50, iterations: int = 10) -> NDArray[np.float32]:
    n = len(x)

    # Start with original values clamped within bounds
    lower = x - T
    upper = x + T
    current = np.clip(np.linspace(x[0] - T, x[-1] + T, n, dtype=np.int32), lower, upper)

    for _ in range(iterations):
        # Smooth with average of neighbors
        smoothed = current.copy()
        for i in range(1, n - 1):
            smoothed[i] = (current[i - 1] + current[i + 1]) / 2
        # Clamp again to legal bounds
        smoothed = np.clip(smoothed, lower, upper)
        # Ensure monotonicity via forward pass
        for i in range(1, n):
            if smoothed[i] < smoothed[i - 1]:
                smoothed[i] = smoothed[i - 1]
        current = smoothed

    return current.round().astype(np.float32)


def compute_time_score(time_diff: NDArray[np.float32]) -> NDArray[np.float32]:
    # Logistic function parameters
    midpoint = 55.0
    steepness = 0.1

    # Compute the time score using the logistic function
    time_scores = 1 / (1 + np.exp(steepness * (time_diff - midpoint)))

    return time_scores.astype(np.float32)


def compute_alternating_penalties(
    candidate_indices: NDArray[np.intp],
    times: NDArray[np.int32],
    columns: NDArray[np.int8],
    time_scores: NDArray[np.float32],
    max_diff_for_triplet_detection: int = 150,
) -> NDArray[np.float32]:
    penalties = np.zeros(len(times), dtype=np.float32)

    for idx in range(len(candidate_indices)):
        i = candidate_indices[idx]
        manip_penalty: float = 0.0

        has_prev = i > 0
        has_prev_prev = i > 1
        has_next = i + 1 < len(times)
        has_next_next = i + 2 < len(times)

        current_col = columns[i]
        next_col = columns[i + 1] if has_next else None

        prev_col = columns[i - 1] if has_prev else None
        prev_prev_col = columns[i - 2] if has_prev_prev else None
        next_next_col = columns[i + 2] if has_next_next else None

        prev_prev_time = times[i - 2] if has_prev_prev else None
        prev_time = times[i - 1] if has_prev else None
        current_time = times[i]
        next_time = times[i + 1] if has_next else None
        next_next_time = times[i + 2] if has_next_next else None

        time_diff_prev_prev = (prev_time - prev_prev_time) if prev_time is not None and prev_prev_time is not None else float("inf")
        time_diff_prev_curr = (current_time - prev_time) if prev_time is not None else float("inf")
        time_diff_curr_next = (next_time - current_time) if next_time is not None else float("inf")
        time_diff_next_next = (next_next_time - next_time) if next_next_time is not None and next_time is not None else float("inf")

        # Initialize triplet check variables
        triplets = []
        triplet_times = []

        valid_triplet_columns = [(1, 2, 1), (2, 1, 2)]

        # Check for valid alternating triplets and store their time sums
        if has_prev_prev and (prev_prev_col, prev_col, current_col) in valid_triplet_columns:
            triplets.append((i - 2, i - 1, i))
            triplet_times.append(time_diff_prev_prev + time_diff_prev_curr)

            if time_diff_prev_prev < max_diff_for_triplet_detection:
                manip_penalty -= float(
                    time_scores[i - 2] / 2 * (max_diff_for_triplet_detection - time_diff_prev_prev) / max_diff_for_triplet_detection
                )
            else:
                manip_penalty -= float((time_diff_prev_prev - max_diff_for_triplet_detection) / max_diff_for_triplet_detection)

        if has_prev and (prev_col, current_col, next_col) in valid_triplet_columns:
            triplets.append((i - 1, i, i + 1))
            triplet_times.append(time_diff_prev_curr + time_diff_curr_next)

        if has_next_next and (current_col, next_col, next_next_col) in valid_triplet_columns:
            triplets.append((i, i + 1, i + 2))
            triplet_times.append(time_diff_curr_next + time_diff_next_next)

            if time_diff_next_next < max_diff_for_triplet_detection:
                manip_penalty -= float(
                    time_scores[i + 2] / 2 * (max_diff_for_triplet_detection - time_diff_next_next) / max_diff_for_triplet_detection
                )
            else:
                manip_penalty -= float((time_diff_next_next - max_diff_for_triplet_detection) / max_diff_for_triplet_detection)

        manip_penalty = min(max(manip_penalty, 0), 1)

        # Find the closest triplet by its time sum
        if triplet_times:
            closest_triplet_index = np.argmin(triplet_times)
            closest_triplet = triplets[closest_triplet_index]
            closest_triplet_time_sum = triplet_times[closest_triplet_index]

            # Use penalty logic on the closest triplet
            i1, i2, i3 = closest_triplet
            avg_time_diff = closest_triplet_time_sum / 2

            # Calculate the penalty based on how close the time differences are
            ratio_to_alternation = min(int(times[i2] - times[i1]), int(times[i3] - times[i2])) / avg_time_diff
            manip_penalty += (ratio_to_alternation - 0.5) * 2

            # Consider surrounding inputs to reinforce or reduce the penalty
            if i1 >= 2:  # Check input before the triplet (i2 - 2)
                prev_prev_col = columns[i1 - 2]
                prev_prev_time = times[i1 - 2]
                time_diff_before_triplet = times[i1] - prev_prev_time

                if (prev_prev_col, columns[i1]) in [(1, 2), (2, 1)]:
                    avg_before_diff = (time_diff_before_triplet + time_diff_prev_prev) / 2
                    if abs(avg_before_diff - avg_time_diff) < avg_time_diff * 0.2:  # Within 20% of avg_time_diff
                        manip_penalty /= 1.2  # Reduce penalty if alternating pattern is consistent

            if i3 + 2 < len(times):  # Check input after the triplet (i2 + 2)
                next_next_col = columns[i3 + 2]
                next_next_time = times[i3 + 2]
                time_diff_after_triplet = next_next_time - times[i3]

                if (columns[i3], next_next_col) in [(1, 2), (2, 1)]:
                    avg_after_diff = (time_diff_next_next + time_diff_after_triplet) / 2
                    if abs(avg_after_diff - avg_time_diff) < avg_time_diff * 0.2:  # Within 20% of avg_time_diff
                        manip_penalty /= 1.2  # Reduce penalty if alternating pattern is consistent

            # Ensure the manip_penalty stays between 0 and 1
            manip_penalty = min(max(manip_penalty, 0), 1)

        penalties[i] = manip_penalty

    return penalties


def adjust_scores_with_nearby_max(
    scores_array: NDArray[np.int8], times: NDArray[np.int32], columns: NDArray[np.int8]
) -> tuple[NDArray[np.int8], NDArray[np.int8]]:
    updated_scores = np.copy(scores_array)
    increments = np.zeros_like(scores_array, dtype=np.int8)

    for i in range(len(scores_array)):
        # Skip if current score is 0 (do not increase scores for fully alternating sequences)
        if scores_array[i] == 0:
            continue

        max_score = scores_array[i]
        max_time = times[i]

        # Check positions i - 2 and i + 2
        for offset in [-2, 2]:
            j = i + offset
            if 0 <= j < len(scores_array):
                if columns[j] != 3:
                    score_j = scores_array[j]
                    time_j = times[j]
                    delta_time = abs(times[i] - time_j)
                    if delta_time <= 300 and score_j > max_score:
                        max_score = score_j
                        max_time = time_j

        # Compute relevance based on delta time
        delta_time = abs(times[i] - max_time)
        relevance = (300.0 - delta_time) / 300.0
        relevance = max(0.0, min(1.0, relevance))

        # Compute increment
        increment = relevance * (max_score - scores_array[i])
        increment = int(round(increment))

        # Update scores and increments
        updated_scores[i] += increment
        increments[i] = increment

    # Ensure scores do not exceed 100
    updated_scores = np.clip(updated_scores, 0, 100)

    return updated_scores, increments


def adjust_consecutive_time_scores(time_scores: NDArray[np.float32]) -> NDArray[np.float32]:
    # Create a boolean mask where the previous time score is higher than the current one
    mask_after = np.roll(time_scores, shift=1) > time_scores
    # Set the first element to False since there's no previous element to compare to
    mask_after[0] = False

    # Create a boolean mask where the next time score is higher than the current one
    mask_before = np.roll(time_scores, shift=-1) > time_scores
    # Set the first element to False since there's no next element to compare to
    mask_before[len(time_scores) - 1] = False

    # Replace the time scores where either mask is True with 0.0
    time_scores[mask_after] = 0.0
    time_scores[mask_before] = 0.0

    return time_scores


def get_manip_jumps_on_hand(
    data: NDArray[np.int32],
    threshold: int = 100,
) -> NDArray[np.int32 | np.int8]:
    times = data[:, 0].astype(np.int32)
    columns = data[:, 1].astype(np.int8)

    time_diffs = np.diff(times).astype(np.int16)

    column_pair_mask = ((columns[:-1] == 1) & (columns[1:] == 2)) | ((columns[:-1] == 2) & (columns[1:] == 1))
    valid_candidates_mask = (time_diffs <= threshold) & column_pair_mask
    candidate_indices = np.where(valid_candidates_mask)[0]

    raw_time_scores = compute_time_score(time_diffs[candidate_indices].astype(np.float32))
    clipped_time_scores = np.clip(raw_time_scores, 0.0, 1.0)

    time_scores = np.zeros(len(data), dtype=np.float32)
    time_scores[candidate_indices] = clipped_time_scores

    type3_indices = np.where(columns == 3)[0]
    time_scores[type3_indices] = 0

    time_scores = adjust_consecutive_time_scores(time_scores)

    alternating_penalties = compute_alternating_penalties(candidate_indices, times, columns, time_scores)

    # Subtract weighted alternating scores from time scores
    final_scores = time_scores - (alternating_penalties * time_scores)

    final_scores_int = np.round(final_scores * 100).astype(np.int8)

    # scores_array, increments = adjust_scores_with_nearby_max(scores_array, times, columns)

    data_with_scores = np.column_stack((times, columns, final_scores_int))

    return data_with_scores


def compute_manip_corrected_hits(hits: list[ChartHit]) -> list[ManipCorrectedHit]:
    all_corrected: list[ManipCorrectedHit] = []

    for hand in [0, 1]:
        hand_hits = [h for h in hits if h.hand == hand]
        if not hand_hits:
            continue

        hand_hits.sort(key=lambda h: h.ms)

        ms = np.array([h.ms for h in hand_hits], dtype=np.int32)
        raw_finger = np.array([h.finger for h in hand_hits], dtype=np.int8)
        manip = np.array([h.manip for h in hand_hits], dtype=np.int8)

        n = len(ms)
        keep_mask = np.ones(n, dtype=bool)

        compress_mask = manip[:-1] > 50
        compress_indices = np.where(compress_mask)[0]

        # Compute values for compressed pairs
        compressed_ms = (ms[compress_indices] + ms[compress_indices + 1]) // 2
        compressed_overlap = np.clip(
            np.minimum(ms[compress_indices] + 50, ms[compress_indices + 1] + 50)
            - np.maximum(ms[compress_indices] - 50, ms[compress_indices + 1] - 50),
            0,
            100,
        )

        # Prepare full arrays
        final_ms = ms.copy()
        final_precision = np.full(n, 100, dtype=np.int32)
        final_finger = np.where(raw_finger >= 2, 3, raw_finger + 1)

        # Apply compressed values to the compressed positions
        final_ms[compress_indices] = compressed_ms
        final_precision[compress_indices] = compressed_overlap
        final_finger[compress_indices] = 3

        # Skip the second hit in each compressed pair
        keep_mask[compress_indices + 1] = False

        # Filter to kept hits
        kept_indices = np.where(keep_mask)[0]
        kept_ms = final_ms[kept_indices]
        kept_precision = final_precision[kept_indices]
        kept_finger = final_finger[kept_indices]

        # Compute gaps
        gaps = np.empty_like(kept_ms)
        gaps[0] = kept_ms[0]
        gaps[1:] = kept_ms[1:] - kept_ms[:-1]

        corrected = [
            ManipCorrectedHit(
                hand=hand,
                finger=int(kept_finger[i]),
                ms=int(kept_ms[i]),
                gap=int(gaps[i]),
                precision=int(kept_precision[i]),
            )
            for i in range(len(kept_ms))
        ]

        all_corrected.extend(corrected)

    return all_corrected


def compute_hit_transitions(hits: list[ManipCorrectedHit]) -> list[ManipCorrectedHitWithTransition]:
    if not hits:
        return []

    # Split and sort by hand
    hands = np.array([h.hand for h in hits])
    fingers = np.array([h.finger for h in hits])
    ms = np.array([h.ms for h in hits])
    gaps = np.array([h.gap for h in hits])
    precisions = np.array([h.precision for h in hits])

    result_transitions = np.full(len(hits), -1, dtype=int)

    for hand in [0, 1]:
        mask = hands == hand
        indices = np.where(mask)[0]
        if len(indices) < 2:
            continue

        # Sort hand-specific hits by time
        sorted_idx = indices[np.argsort(ms[indices])]
        f = fingers[sorted_idx]

        # Shift arrays
        f1 = f[:-1]
        f2 = f[1:]
        transitions = np.full(len(f1), -1, dtype=int)

        # Apply rules
        transitions[(f1 != 3) & (f2 != 3) & (f1 != f2)] = 0  # trill
        transitions[(f1 != 3) & (f2 != 3) & (f1 == f2)] = 1  # jack
        transitions[(f1 == 3) & (f2 != 3)] = 2  # jump to single
        transitions[(f1 != 3) & (f2 == 3)] = 3  # single to jump
        transitions[(f1 == 3) & (f2 == 3)] = 4  # jumpstream

        result_transitions[sorted_idx[:-1]] = transitions

    # Pack result
    result = [
        ManipCorrectedHitWithTransition(
            hand=int(hands[i]),
            finger=int(fingers[i]),
            ms=int(ms[i]),
            gap=int(gaps[i]),
            precision=int(precisions[i]),
            transition=int(result_transitions[i]),
        )
        for i in range(len(hits))
    ]

    return result
