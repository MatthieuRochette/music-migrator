import sys
import logging

from .music_migrator import MusicMigratorCli, MusicMigratorGui, MusicMigrator
from .utils import cli_args
from .utils.custom_logger import logger, _formatter

_instance: MusicMigrator


def main_gui():
    global _instance
    # Not implemented yet, will come once the CLI version is finished.
    logger.info("Launching GUI version.")
    _instance = MusicMigratorGui()
    _instance.main()


def main_cli():
    global _instance
    # Configure logging
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(_formatter)
    logger.addHandler(stream_handler)

    logger.info("Launching CLI version.")

    # Hanle CLI arguments
    args = cli_args.parse_arguments()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging mode is activated.")
    if args.gui:
        logger.info("Opening GUI version from CLI version.")
        return main_gui()

    _instance = MusicMigratorCli()
    _instance.main()


def main():
    if sys.stdin and sys.stdin.isatty():
        main_cli()
    else:
        main_gui()
