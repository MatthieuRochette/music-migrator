import logging

logger = logging.getLogger("MusicMigrator")
logger.setLevel(logging.INFO)

_file_handler = logging.FileHandler(".music_migrator_logs.txt", encoding="utf-8")
_file_handler.setLevel(logging.INFO)

_formatter = logging.Formatter(
    fmt="%(asctime)s | %(name)s - %(levelname)s: %(message)s"
)
_file_handler.setFormatter(_formatter)

logger.addHandler(_file_handler)
