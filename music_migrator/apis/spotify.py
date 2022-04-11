import spotipy
from spotipy.oauth2 import SpotifyOAuth

from music_migrator.config import config


class SpotifyApi:
    """A class used as an abstraction layer for the underlying Spotify API implementation."""

    scopes = [
        "user-library-read",
        "playlist-read-private",
        "playlist-read-collaborative",
        "user-top-read",
    ]

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        self._client_id = (
            config["spotify"]["client_id"] if client_id is None else client_id
        )
        self._client_secret = (
            config["spotify"]["client_secret"]
            if client_secret is None
            else client_secret
        )
        self._redirect_uri = (
            config["spotify"]["redirect_uri"] if redirect_uri is None else redirect_uri
        )

        self._auth_manager = SpotifyOAuth(
            client_id=self._client_id,
            client_secret=self._client_secret,
            scope=self.scopes,
            redirect_uri=self._redirect_uri,
        )

        self._api = spotipy.Spotify(auth_manager=self._auth_manager)

    def get_favorites(self, result_limit=-1, _limit_per_request=20) -> list:
        global_result = []
        result = self._api.current_user_saved_tracks(limit=_limit_per_request)
        count = len(result["items"])
        global_result.append(result)

        while result and (count < result_limit or result_limit == -1):
            count += len(result["items"])
            if result["next"]:
                result = self._api.next(result)
                global_result.append(result)
            else:
                result = None

        return global_result

    def pretty_print_results_tracks(self, results: list):
        print(
            "|-------------------------------------------------------------------------------------------------------------------------------------------------------|"
        )
        print(
            "|"
            + "N°".center(7)
            + "|"
            + "Track ID".center(27)
            + "|"
            + "Track name".center(52)
            + "|"
            + "Artists".center(62)
            + "|"
        )
        print(
            "|-------------------------------------------------------------------------------------------------------------------------------------------------------|"
        )
        for favorites in results:
            for i, favorite in enumerate(favorites["items"]):
                print(
                    f"| {str(i + 1 + favorites['offset']).ljust(5)} | {str(favorite['track']['id']).ljust(25)} | {str(favorite['track']['name']).ljust(50)} | {str([artist['name'] for artist in favorite['track']['artists']]).ljust(60)} |"
                )
        print(
            "|-------------------------------------------------------------------------------------------------------------------------------------------------------|"
        )
