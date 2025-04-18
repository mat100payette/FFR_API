import json
from pathlib import Path

from scipy.stats import spearmanr


def analyze_estimates(file_path_str: str):
    file_path = Path(file_path_str)

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Expected a list at the top level of the JSON file.")

    # Filter entries
    data = [entry for entry in data if entry[2] != 0 and entry[0] not in [2605, 3347, 3922]]

    total = len(data)
    total_abs_diff = 0.0
    max_diff = float("-inf")
    max_entry = None

    for entry in data:
        diff = abs(entry[2] - entry[3])
        total_abs_diff += diff

        if diff > max_diff:
            max_diff = diff
            max_entry = entry

    avg_abs_diff = total_abs_diff / total if total > 0 else 0.0

    print(f"Number of entries: {total}")
    print(f"Average absolute difference: {avg_abs_diff:.4f}")

    if max_entry:
        print(f"Max absolute difference: {max_diff:.4f}")
        print(f"Occurred on chart: ID={max_entry[0]}, Name='{max_entry[1]}', Difficulty={max_entry[2]}, Estimate={max_entry[3]}")

    # Sort by absolute difference descending
    sorted_data = sorted(data, key=lambda entry: abs(entry[2] - entry[3]), reverse=True)

    # Build output file path with _sorted suffix
    sorted_file_path = file_path.with_name(file_path.stem + "_sorted" + file_path.suffix)

    with sorted_file_path.open("w", encoding="utf-8") as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)

    print(f"Sorted output written to: {sorted_file_path}")


def compare_orderings(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    difficulties = [entry[2] for entry in data]
    estimates = [entry[3] for entry in data]

    correlation, _ = spearmanr(difficulties, estimates)

    print(f"Spearman correlation (ranking similarity): {correlation:.4f}")
