from .apis import SpotifyApi, DeezerApi

from .utils.custom_logger import logger


class MusicMigrator:
    def setup(self):
        self.spotify = SpotifyApi()
        self.deezer = DeezerApi()

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
        super().setup()
        favorites = self.spotify.get_favorites(result_limit=20)
        self.spotify.pretty_log_results_tracks(favorites)


class MusicMigratorGui(MusicMigrator):
    def main(self):
        # super().setup()  # uncomment this when implementing this class
        raise NotImplementedError(
            "The Gui version will wait until the CLI one is done, as the focus is on the base class and a CLI is faster to implement."
        )
