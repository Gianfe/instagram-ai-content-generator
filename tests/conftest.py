"""Shared fixtures for tests that use Instagram configuration."""

from __future__ import annotations

import pytest

from instagram_content_creator.config import InstagramConfig


@pytest.fixture
def set_instagram_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("instagram_content_creator.config.load_dotenv", lambda *args, **kwargs: False)
    monkeypatch.setenv("INSTAGRAM_APP_ID", "test-app-id")
    monkeypatch.setenv("INSTAGRAM_USER_ID", "123456789")
    monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", "test-access-token")
    monkeypatch.delenv("INSTAGRAM_API_HOST", raising=False)


@pytest.fixture
def config(set_instagram_env: None) -> InstagramConfig:
    return InstagramConfig.from_env()
