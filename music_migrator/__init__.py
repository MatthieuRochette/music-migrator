import sys
import logging

from .utils.custom_logger import logger


def main_gui():
    # Not implemented yet, will come once the CLI version is finished.
    logger.info("Launching GUI version.")


def main_cli():
    import argparse

    logger.addHandler(logging.StreamHandler())
    logger.info("Launching CLI version.")

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
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Test")
    if args.gui:
        logger.info("Opening GUI version from CLI version.")
        return main_gui()


def main():

    if sys.stdin and sys.stdin.isatty():
        main_cli()
    else:
        main_gui()
