from time import perf_counter

from deezer import Track as DeezerTrack

from .apis import DeezerApi, SpotifyApi
from .apis.spotify import SpotifyTrack
from .utils.custom_logger import logger
from .utils.enums import SearchResultCertaintyEnum


class MusicMigrator:
    def __init__(self):
        self.spotify = SpotifyApi()
        self.deezer = DeezerApi()

    def find_deezer_tracks_from_spotify_favorites(
        self, result_limit=-1
    ) -> list[tuple[SpotifyTrack, DeezerTrack, SearchResultCertaintyEnum]]:
        t1 = perf_counter()

        result_list = []
        favorites_paginated = self.spotify.get_favorites(result_limit=result_limit)
        self.spotify.pretty_log_results_tracks(favorites_paginated)
        for favorites_page in favorites_paginated:
            for favorite in favorites_page["items"]:
                result_list.append(
                    (
                        favorite,  # bit of unpacking black magic here
                        *self.deezer.search_best_match_for_spotify_track(
                            favorite["track"]
                        ),
                    )
                )

        logger.info(f"Execution time: {perf_counter() - t1}")
        return result_list

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
        tracks_found = self.find_deezer_tracks_from_spotify_favorites(result_limit=100)
        sure_tracks = [
            track
            for track in tracks_found
            if track[2] == SearchResultCertaintyEnum.SURE
        ]
        unsure_tracks = [
            track
            for track in tracks_found
            if track[2] == SearchResultCertaintyEnum.NOT_SURE
        ]
        not_found_tracks = [
            track
            for track in tracks_found
            if track[2] == SearchResultCertaintyEnum.NOT_FOUND
        ]
        logger.info(
            f"There are {len(sure_tracks)} perfectly matching tracks. You do not need to review them."
        )
        logger.info(
            f"There are {len(unsure_tracks)} that couldn't be matched perfectly to a result on Deezer. Please review them manually."
        )
        logger.info(
            f"There are {len(not_found_tracks)} that had no match at all. Please search manually or be ready to say goodbye :') ."
        )
        # print(len(sure_tracks), len(unsure_tracks), len(not_found_tracks)))


class MusicMigratorGui(MusicMigrator):
    def main(self):
        raise NotImplementedError(
            "The Gui version will wait until the CLI one is done, as the focus is on the base class and a CLI is faster to implement."
        )
