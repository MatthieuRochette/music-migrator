import argparse


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-g",
        "--gui",
        help="Lauch the GUI version instead of the CLI one",
        action="store_true",
    )
    parser.add_argument(
        "--debug", help="Print debugging (in CLI only)", action="store_true"
    )
    return parser.parse_args()
