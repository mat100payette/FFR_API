import multiprocessing
from src.controller import call_api
from services.service import set_api_key
from utils.args import parse_args


def main():
    args = parse_args(set_api_key)
    api_response = call_api(args)
    a = 1

if __name__ == '__main__':
    multiprocessing.freeze_support()
    try:
        main()
        print('Done.')
    except Exception as e:
        print(f'Error: {e}')