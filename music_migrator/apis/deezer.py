# DISCLAIMER
# THIS CODE IS HEAVILY INSPIRED FROM THE SPOTIPY LIBRARY'S SportifyOAuth class
# https://github.com/plamere/spotipy/blob/master/spotipy/oauth2.py

import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlencode, urlparse
import os.path

import requests

import deezer

from ..config import config
from ..utils.custom_logger import logger


class DeezerOauthError(Exception):
    """Error during Auth Code or Implicit Grant flow"""

    def __init__(self, message, error=None, error_description=None, *args, **kwargs):
        self.error = error
        self.error_description = error_description
        self.__dict__.update(kwargs)
        super(DeezerOauthError, self).__init__(message, *args, **kwargs)


class DeezerRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.auth_code = self.server.error = None
        try:
            auth_code = DeezerApi.parse_auth_response_url(self.path)
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

    OAUTH_AUTHORIZE_URL = "https://connect.deezer.com/oauth/auth.php"
    OAUTH_TOKEN_URL = "https://connect.deezer.com/oauth/access_token.php"
    OAUTH_TOKEN_SAVE_PATH = ".deezer_token.cache"

    def __init__(self, *args, **kwargs) -> None:
        self._client = deezer.Client(
            app_id=config["deezer"]["client"]["id"],
            app_secret=config["deezer"]["client"]["secret"],
            *args,
            **kwargs,
        )

        # perform user authentication
        self._oauth_token = self._get_oauth_token_from_storage()
        if self._oauth_token is None:
            self._oauth_token = self._use_oauth2()
        self._save_oauth_token()
        logger.info("User successfully logged in to Deezer.")

    def _get_oauth_token_from_storage(self) -> str | None:
        try:
            with open(self.OAUTH_TOKEN_SAVE_PATH, "r") as token_cache:
                token = token_cache.read()
                if not token:
                    raise ValueError("Token cache file is empty.")
        except (FileNotFoundError, ValueError) as e:
            logger.info("No Deezer token saved.")
            logger.error(e.strerror)
            return None
        else:
            logger.info("Deezer token successfully retrieved.")
            return token

    def _save_oauth_token(self):
        with open(self.OAUTH_TOKEN_SAVE_PATH, "w") as token_cache:
            token_cache.write(self._oauth_token)
        logger.info("Deezer OAuth token successfully saved.")

    def _get_authorize_url(self):
        """Gets the URL to use to authorize this app"""
        payload = {
            "app_id": self._client.app_id,
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
            "app_id": self._client.app_id,
            "secret": self._client.app_secret,
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

    def _use_oauth2(self) -> str:
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
