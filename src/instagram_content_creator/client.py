"""Thin HTTP wrapper around the Meta Graph API."""

from __future__ import annotations

from typing import Any, Optional

import requests

from .config import InstagramConfig
from .exceptions import InstagramAPIError

REQUEST_TIMEOUT_SECONDS = 30


class GraphAPIClient:
    """Minimal client for making authenticated calls to the Graph API.

    The host (``graph.instagram.com`` vs ``graph.facebook.com``) depends on
    which login flow issued the access token; see :mod:`.config`.
    """

    def __init__(self, config: InstagramConfig, session: Optional[requests.Session] = None) -> None:
        self.config = config
        self.session = session or requests.Session()
        self.base_url = f"https://{config.host}/{config.api_version}"

    def post(self, path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return self._request("POST", path, params)

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return self._request("GET", path, params)

    def _request(self, method: str, path: str, params: Optional[dict[str, Any]]) -> dict[str, Any]:
        request_params = dict(params or {})
        request_params["access_token"] = self.config.access_token
        url = f"{self.base_url}/{path.lstrip('/')}"

        if method == "GET":
            response = self.session.get(url, params=request_params, timeout=REQUEST_TIMEOUT_SECONDS)
        else:
            response = self.session.post(url, data=request_params, timeout=REQUEST_TIMEOUT_SECONDS)

        return self._handle_response(response)

    @staticmethod
    def _handle_response(response: requests.Response) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError:
            data = {}

        if response.status_code >= 400:
            error = data.get("error", {}) if isinstance(data, dict) else {}
            message = error.get(
                "message", f"Graph API request failed with status {response.status_code}"
            )
            raise InstagramAPIError(message, response=data)

        return data
