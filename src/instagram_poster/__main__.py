from __future__ import annotations

import requests

from .config import InstagramConfig


class InstagramAPIError(RuntimeError):
    """Raised when the Instagram Graph API returns a failure."""


class InstagramGraphClient:
    """Client for creating a simple image post on Instagram."""

    DEFAULT_IMAGE_URL = "https://placehold.co/1200x1200/000000/FFFFFF.png?text=Hello+word"

    def __init__(self, config: InstagramConfig):
        self.config = config

    def _request(self, method: str, path: str, *, payload: dict | None = None, params: dict | None = None):
        url = f"{self.config.base_url}/{path}"
        request_params = {"access_token": self.config.access_token}
        if params:
            request_params.update(params)

        response = requests.request(method, url, params=request_params, json=payload, timeout=30)

        try:
            result = response.json()
        except ValueError:
            result = {}

        if not response.ok or (isinstance(result, dict) and "error" in result):
            error = result.get("error", {}) if isinstance(result, dict) else {}
            message = error.get("message", response.text)
            raise InstagramAPIError(f"Instagram API request failed: {message}")

        return result

    def create_post(self, caption: str, image_url: str | None = None) -> dict:
        normalized_caption = (caption or "").strip()
        if not normalized_caption:
            raise ValueError("caption cannot be empty")

        resolved_image_url = image_url or self.DEFAULT_IMAGE_URL
        payload = {
            "media_type": "IMAGE",
            "image_url": resolved_image_url,
            "caption": normalized_caption,
        }

        create_response = self._request("POST", f"{self.config.user_id}/media", payload=payload)
        creation_id = create_response.get("id")
        if not creation_id:
            raise InstagramAPIError("Instagram media creation did not return a valid creation_id")

        publish_response = self._request(
            "POST",
            f"{self.config.user_id}/media_publish",
            payload={"creation_id": creation_id},
        )
        return publish_response


def create_default_client() -> InstagramGraphClient:
    return InstagramGraphClient(InstagramConfig.from_env())
