import multiprocessing as mp

from controller import run
from utils.api import set_api_key
from utils.args_parser import parse_args


def main():
    args = parse_args(set_api_key)
    _result = run(args)
    _a = 1


if __name__ == "__main__":
    mp.freeze_support()
    try:
        main()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
