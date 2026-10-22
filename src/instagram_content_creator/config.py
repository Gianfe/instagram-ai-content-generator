"""Configuration loading for the Instagram Graph API client."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_API_VERSION = "v21.0"

# Instagram API with Instagram Login (Business Login) issues "IGAA..." user tokens
# that only work against graph.instagram.com. Facebook Page tokens ("EAA...") used by
# the Instagram API with Facebook Login must go through graph.facebook.com instead.
HOST_INSTAGRAM_LOGIN = "graph.instagram.com"
HOST_FACEBOOK_LOGIN = "graph.facebook.com"

_REQUIRED_ENV_VARS = (
    "INSTAGRAM_APP_ID",
    "INSTAGRAM_USER_ID",
    "INSTAGRAM_ACCESS_TOKEN",
)


def _default_host_for_token(access_token: str) -> str:
    return HOST_FACEBOOK_LOGIN if access_token.startswith("EAA") else HOST_INSTAGRAM_LOGIN


@dataclass(frozen=True)
class InstagramConfig:
    """Holds the credentials required to call the Instagram Graph API."""

    app_id: str
    user_id: str
    access_token: str
    api_version: str = DEFAULT_API_VERSION
    host: str = ""

    def __post_init__(self) -> None:
        if not self.host:
            object.__setattr__(self, "host", _default_host_for_token(self.access_token))

    @classmethod
    def from_env(cls, *, api_version: str = DEFAULT_API_VERSION) -> "InstagramConfig":
        """Build a config from environment variables (loads a local .env file if present)."""
        load_dotenv()

        values = {name: os.getenv(name) for name in _REQUIRED_ENV_VARS}
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise OSError(
                "Missing required environment variable(s): " + ", ".join(missing)
            )

        return cls(
            app_id=values["INSTAGRAM_APP_ID"],  # type: ignore[arg-type]
            user_id=values["INSTAGRAM_USER_ID"],  # type: ignore[arg-type]
            access_token=values["INSTAGRAM_ACCESS_TOKEN"],  # type: ignore[arg-type]
            api_version=api_version,
            host=os.getenv("INSTAGRAM_API_HOST", ""),
        )
