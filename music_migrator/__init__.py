import sys
import logging

from .music_migrator import MusicMigrator
from .utils import cli_args
from .utils.custom_logger import logger

_instance = MusicMigrator()


def main_gui():
    # Not implemented yet, will come once the CLI version is finished.
    logger.info("Launching GUI version.")
    _instance.gui()


def main_cli():
    # Configure logging
    logger.addHandler(logging.StreamHandler())
    logger.info("Launching CLI version.")

    # Hanle CLI arguments
    args = cli_args.parse_arguments()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.gui:
        logger.info("Opening GUI version from CLI version.")
        return main_gui()

    _instance.cli()


def main():
    if sys.stdin and sys.stdin.isatty():
        main_cli()
    else:
        main_gui()
