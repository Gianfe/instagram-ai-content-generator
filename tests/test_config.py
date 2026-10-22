"""Tests for InstagramConfig.from_env()."""

from __future__ import annotations

import pytest

from instagram_content_creator.config import InstagramConfig


def test_from_env_builds_config(set_instagram_env: None) -> None:
    config = InstagramConfig.from_env()

    assert config.app_id == "test-app-id"
    assert config.user_id == "123456789"
    assert config.access_token == "test-access-token"
    assert config.api_version == "v21.0"


@pytest.mark.parametrize(
    ("access_token", "expected_host"),
    [
        ("IGAAabc123", "graph.instagram.com"),
        ("EAAabc123", "graph.facebook.com"),
    ],
)
def test_host_is_inferred_from_access_token_prefix(access_token: str, expected_host: str) -> None:
    config = InstagramConfig(app_id="app", user_id="user", access_token=access_token)

    assert config.host == expected_host


def test_host_can_be_overridden_via_env(monkeypatch: pytest.MonkeyPatch, set_instagram_env: None) -> None:
    monkeypatch.setenv("INSTAGRAM_API_HOST", "graph.facebook.com")

    config = InstagramConfig.from_env()

    assert config.host == "graph.facebook.com"


def test_from_env_raises_when_missing_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    # ignore any real local .env file so the test is hermetic
    monkeypatch.setattr("instagram_content_creator.config.load_dotenv", lambda *a, **k: False)
    monkeypatch.delenv("INSTAGRAM_APP_ID", raising=False)
    monkeypatch.delenv("INSTAGRAM_USER_ID", raising=False)
    monkeypatch.delenv("INSTAGRAM_ACCESS_TOKEN", raising=False)

    with pytest.raises(OSError, match="INSTAGRAM_APP_ID"):
        InstagramConfig.from_env()


def test_from_env_reports_only_missing_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    # ignore any real local .env file so the test is hermetic
    monkeypatch.setattr("instagram_content_creator.config.load_dotenv", lambda *a, **k: False)
    monkeypatch.setenv("INSTAGRAM_APP_ID", "test-app-id")
    monkeypatch.delenv("INSTAGRAM_USER_ID", raising=False)
    monkeypatch.delenv("INSTAGRAM_ACCESS_TOKEN", raising=False)

    with pytest.raises(OSError) as exc_info:
        InstagramConfig.from_env()

    message = str(exc_info.value)
    assert "INSTAGRAM_USER_ID" in message
    assert "INSTAGRAM_ACCESS_TOKEN" in message
    assert "INSTAGRAM_APP_ID" not in message
