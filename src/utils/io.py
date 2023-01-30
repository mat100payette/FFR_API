import json
from pathlib import Path

import compress_json

JSON_EXT = '.json'
LZMA_EXT = '.lzma'

def write_compressed_json_to_file(json_data, file_name: str):
    full_file_name = f'{file_name}{LZMA_EXT}'
    print(f'Writing to file: {full_file_name}')

    compress_json.dump(json_data, full_file_name)

def write_json_to_file(bytes, file_name: str):
    full_file_name = f'{file_name}{JSON_EXT}'
    print(f'Writing to file: {full_file_name}')

    Path(full_file_name).parents[0].mkdir(mode=0o777, parents=True, exist_ok=True)
    with open(full_file_name, 'w+', encoding='utf-8') as f:
        json.dump(bytes, f, ensure_ascii=False)