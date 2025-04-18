import json
import lzma
import os
from pathlib import Path

from platformdirs import user_data_dir

_APP_CACHE_NAME = "ChartVisualizer"

_CHARTS_DIR = "charts"
_COMPRESSED_DIR = "compressed"
_EXTENDED_DIR = "extended"

JSON_EXT = ".json"
LZMA_EXT = ".lzma"

type StrOrPath = str | Path


def default_cache_path():
    return Path(user_data_dir(_APP_CACHE_NAME, appauthor=False))


def charts_dir_path():
    return Path(_CHARTS_DIR)


def compressed_dir_path():
    return Path(_COMPRESSED_DIR)


def extended_dir_path():
    return Path(_EXTENDED_DIR)


def _ensure_extension(file_name: StrOrPath, expected_ext: str) -> str:
    """Ensure that the file has the correct extension."""
    file_path = Path(file_name)
    if not file_path.suffix == expected_ext:
        file_path = file_path.with_suffix(expected_ext)
    return str(file_path)


def write_compressed_json_to_file(json_data, file_name: StrOrPath):
    full_file_name = _ensure_extension(file_name, LZMA_EXT)
    print(f"Writing to file: {full_file_name}")

    os.makedirs(os.path.dirname(full_file_name), exist_ok=True)

    with lzma.open(full_file_name, mode="wt", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False)


def write_json_to_file(json_data, file_name: StrOrPath):
    full_file_name = _ensure_extension(file_name, JSON_EXT)
    print(f"Writing to file: {full_file_name}")

    # Ensure parent directories exist
    file_path = Path(full_file_name)
    file_path.parent.mkdir(mode=0o777, parents=True, exist_ok=True)

    with open(file_path, "w+", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False)


def load_compressed_json_from_file(file_name: StrOrPath):
    full_file_name = _ensure_extension(file_name, LZMA_EXT)
    print(f"Loading from file: {full_file_name}")

    with lzma.open(full_file_name, mode="rt", encoding="utf-8") as f:
        return f.read()


def load_json_from_file(file_name: StrOrPath):
    full_file_name = _ensure_extension(file_name, JSON_EXT)
    print(f"Loading from file: {full_file_name}")

    with open(full_file_name, "r", encoding="utf-8") as f:
        return f.read()


def build_chart_filename(directory: str, extended: bool, compressed: bool, level_id: int) -> Path:
    # Create the base directory path
    base_dir = Path(directory)

    # Append the subdirectories based on the flags
    raw_subdir = _EXTENDED_DIR if extended else ""
    subdir = (Path(raw_subdir) / _COMPRESSED_DIR) if compressed else Path(raw_subdir)

    # Build the full path with the chart file name
    filename = base_dir / _CHARTS_DIR / subdir / f"chart_{level_id}"

    return filename
