import logging

logger = logging.getLogger("MusicMigrator")
logger.setLevel(logging.INFO)

_file_handler = logging.FileHandler(".music_migrator_logs.txt")
_file_handler.setLevel(logging.INFO)
logger.addHandler(_file_handler)
