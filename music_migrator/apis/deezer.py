# DISCLAIMER
# THIS CODE IS HEAVILY INSPIRED FROM THE SPOTIPY LIBRARY'S SportifyOAuth class
# https://github.com/plamere/spotipy/blob/master/spotipy/oauth2.py

import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlencode, urlparse

import requests

import deezer
from deezer import Track as DeezerTrack
from deezer.exceptions import DeezerErrorResponse
from deezer.pagination import PaginatedList

from ..config import config
from ..utils.custom_logger import logger
from ..utils.enums import SearchResultCertaintyEnum


class DeezerOauthError(Exception):
    """Error during Auth Code or Implicit Grant flow"""

    def __init__(self, message, error=None, error_description=None, *args, **kwargs):
        self.error = error
        self.error_description = error_description
        self.__dict__.update(kwargs)
        super(DeezerOauthError, self).__init__(message, *args, **kwargs)


class DeezerOauth:
    OAUTH_AUTHORIZE_URL = "https://connect.deezer.com/oauth/auth.php"
    OAUTH_TOKEN_URL = "https://connect.deezer.com/oauth/access_token.php"
    OAUTH_TOKEN_SAVE_PATH = ".deezer_token.cache"

    def get_oauth_token_from_storage(self) -> str | None:
        try:
            with open(self.OAUTH_TOKEN_SAVE_PATH, "r") as token_cache:
                token = token_cache.read()
                if not token:
                    raise ValueError("Token cache file is empty.")
        except (FileNotFoundError, ValueError) as e:
            logger.info("No Deezer token saved.")
            logger.error(str(e))
            return None
        else:
            logger.info("Deezer token successfully retrieved.")
            return token

    def save_oauth_token(self, oauth_token: str):
        with open(self.OAUTH_TOKEN_SAVE_PATH, "w") as token_cache:
            token_cache.write(oauth_token)
        logger.info("Deezer OAuth token successfully saved.")

    def _get_authorize_url(self) -> str:
        """Gets the URL to use to authorize this app"""
        payload = {
            "app_id": config["deezer"]["client"]["id"],
            "redirect_uri": f"http://{config['deezer']['oauth']['host']}:{config['deezer']['oauth']['port']}{config['deezer']['oauth']['callback_route']}",
            "perms": "basic_access,manage_library,offline_access",
        }
        urlparams = urlencode(payload)
        return f"{self.OAUTH_AUTHORIZE_URL}?{urlparams}"

    def _open_auth_url(self):
        auth_url = self._get_authorize_url()
        try:
            webbrowser.open(auth_url)
            logger.info("Opened %s in your browser", auth_url)
        except webbrowser.Error:
            logger.error("Please navigate here: %s", auth_url)

    def _authenticate(self):
        self._http_server = HTTPServer(
            (config["deezer"]["oauth"]["host"], config["deezer"]["oauth"]["port"]),
            DeezerRequestHandler,
        )
        self._http_server.allow_reuse_address = True
        self._http_server.auth_code = None
        self._http_server.auth_token_form = None
        self._http_server.error = None

        self._open_auth_url()
        self._http_server.handle_request()

        if self._http_server.error is not None:
            raise self._http_server.error
        elif self._http_server.auth_code is not None:
            return self._http_server.auth_code
        else:
            raise DeezerOauthError(
                "Server listening on localhost has not been accessed"
            )

    def _get_token_url(self, code: str) -> str:
        payload = {
            "app_id": config["deezer"]["client"]["id"],
            "secret": config["deezer"]["client"]["secret"],
            "code": code,
            "output": "json",
        }
        urlparams = urlencode(payload)
        return f"{self.OAUTH_TOKEN_URL}?{urlparams}"

    def _request_token_to_api_from_code(self, code: str) -> str:
        url = self._get_token_url(code)
        response = requests.get(url)
        if response.status_code != 200:
            raise DeezerOauthError(
                f"Error while getting the token, code {response.status_code}: {response.text}"
            )
        body = response.json()
        return body["access_token"]

    def use_oauth2(self) -> str:
        code = self._authenticate()
        oauth_token = self._request_token_to_api_from_code(code)
        return oauth_token

    @staticmethod
    def parse_auth_response_url(url):
        query_s = urlparse(url).query
        form = dict(parse_qsl(query_s))
        if "error_reason" in form:
            raise DeezerOauthError(
                "Received error from auth server: " "{}".format(form["error_reason"]),
                error=form["error_reason"],
            )
        return form.get("code")


class DeezerRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.auth_code = self.server.error = None
        try:
            auth_code = DeezerOauth.parse_auth_response_url(self.path)
            self.server.auth_code = auth_code
        except DeezerOauthError as error:
            self.server.error = error

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        if self.server.auth_code:
            status = "successful"
        elif self.server.error:
            status = "failed ({})".format(self.server.error)
        else:
            self._write("<html><body><h1>Invalid request</h1></body></html>")
            return

        self._write(
            """<html>
<script>
window.close()
</script>
<body>
<h1>Authentication status: {}</h1>
This window can be closed.
<script>
window.close()
</script>
<button class="closeButton" style="cursor: pointer" onclick="window.close();">Close Window</button>
</body>
</html>""".format(
                status
            )
        )

    def _write(self, text):
        return self.wfile.write(text.encode("utf-8"))

    def log_message(self, format, *args):
        return


class DeezerApi:
    """A class used as an abstraction layer for the underlying Deezer API implementation."""

    def __init__(self, *args, **kwargs) -> None:
        self._client = deezer.Client(
            app_id=config["deezer"]["client"]["id"],
            app_secret=config["deezer"]["client"]["secret"],
            *args,
            **kwargs,
        )

        self._oauth = DeezerOauth()

        # perform user authentication
        self._oauth_token = self._oauth.get_oauth_token_from_storage()
        if self._oauth_token is None:
            self._oauth_token = self._oauth.use_oauth2()
        self._oauth.save_oauth_token(self._oauth_token)
        logger.info("User successfully logged in to Deezer.")

    def search(self, *args, **kwargs) -> PaginatedList[deezer.Track]:
        response: PaginatedList = self._client.search(*args, **kwargs)
        try:
            response[
                0
            ]  # lazy load the result, which raises potential Exception from the API
            return response  # return if no Exception raised
        except IndexError:
            return response  # ignore IndexError, empty results are valid search results
        except DeezerErrorResponse as e:
            from time import sleep

            # handle the quota limit exception
            if e.json_data["error"]["code"] == 4:
                logger.warn("Deezer API quota limit attained. Waiting 3 seconds.")
                sleep(3)
                return self.search(*args, **kwargs)
            else:
                raise e

    def search_best_match_for_spotify_track(
        self, spotify_track: dict
    ) -> tuple[DeezerTrack, SearchResultCertaintyEnum]:
        naive_search_query = " ".join(
            [
                spotify_track["name"],
                *[artist["name"] for artist in spotify_track["artists"]],
            ]
        )
        naive_search_results = self.search(query=naive_search_query)
        try:
            result: deezer.Track = naive_search_results[0]
        except IndexError:
            logger.info(
                f"No result for track '{spotify_track['name']}' by {spotify_track['artists'][0]['name']}."
            )
            return (None, SearchResultCertaintyEnum.NOT_FOUND)
        else:
            certainty = (
                SearchResultCertaintyEnum.NOT_SURE
                if result.title != spotify_track["name"]
                or result.artist.name != spotify_track["artists"][0]["name"]
                else SearchResultCertaintyEnum.SURE
            )
            logger.info(
                f"Found '{result.title}' by {result.artist.name} ({result.preview}) \t{'| Not sure' if certainty == SearchResultCertaintyEnum.NOT_SURE else '| Sure'}"
            )
            return (result, certainty)
