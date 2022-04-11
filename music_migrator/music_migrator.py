from .apis import SpotifyApi, DeezerApi

from .utils.custom_logger import logger


class MusicMigrator:
    spotify = SpotifyApi()
    deezer = DeezerApi()

    def cli(self):
        favorites = self.spotify.get_favorites(result_limit=100)
        self.spotify.pretty_print_results_tracks(favorites)

    def gui(self):
        pass
