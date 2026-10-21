from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class InstagramConfig:
    """Instagram Graph API configuration loaded from environment variables."""

    app_id: str
    user_id: str
    access_token: str
    api_version: str = "v20.0"

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "InstagramConfig":
        data = os.environ if env is None else env
        required = {
            "INSTAGRAM_APP_ID": data.get("INSTAGRAM_APP_ID"),
            "INSTAGRAM_USER_ID": data.get("INSTAGRAM_USER_ID"),
            "INSTAGRAM_ACCESS_TOKEN": data.get("INSTAGRAM_ACCESS_TOKEN"),
        }

        missing = [name for name, value in required.items() if not value or not value.strip()]
        if missing:
            missing_str = ", ".join(missing)
            raise ValueError(f"Missing required env vars: {missing_str}")

        return cls(
            app_id=required["INSTAGRAM_APP_ID"].strip(),
            user_id=required["INSTAGRAM_USER_ID"].strip(),
            access_token=required["INSTAGRAM_ACCESS_TOKEN"].strip(),
        )

    @property
    def base_url(self) -> str:
        return f"https://graph.facebook.com/{self.api_version}"
