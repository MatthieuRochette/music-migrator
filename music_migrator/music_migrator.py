from time import perf_counter

from .apis import DeezerApi, SpotifyApi
from .utils.custom_logger import logger


class MusicMigrator:
    def __init__(self):
        self.spotify = SpotifyApi()
        self.deezer = DeezerApi()

    def migrate_favorites_from_spotify_to_deezer(self):
        t1 = perf_counter()
        self.spotify.pretty_log_results_tracks(favorites_results)
        for favorites in favorites_results:
            for favorite in favorites["items"]:
                self.deezer.search_best_match_for_spotify_track(favorite["track"])
        logger.info(f"Execution time: {perf_counter() - t1}")

    def main(self):
        logger.fatal("Calling main function in the base MusicMigrator class.")
        logger.fatal(
            "This shoud never be called, as the base class is meant for re-use in other classes/programs."
        )
        logger.fatal(
            "If you mean to implement the MusicMigrator by itself, use the MusicMigratorCli or MusicMigratorGui classes."
        )
        raise NotImplementedError()


class MusicMigratorCli(MusicMigrator):
    def main(self):
        self.migrate_favorites_from_spotify_to_deezer()


class MusicMigratorGui(MusicMigrator):
    def main(self):
        raise NotImplementedError(
            "The Gui version will wait until the CLI one is done, as the focus is on the base class and a CLI is faster to implement."
        )
