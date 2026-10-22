"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from instagram_content_creator.config import InstagramConfig


@pytest.fixture
def config() -> InstagramConfig:
    return InstagramConfig(
        app_id="test-app-id",
        user_id="123456789",
        access_token="test-access-token",
        api_version="v21.0",
    )


@pytest.fixture
def set_instagram_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INSTAGRAM_APP_ID", "test-app-id")
    monkeypatch.setenv("INSTAGRAM_USER_ID", "123456789")
    monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", "test-access-token")
