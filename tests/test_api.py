"""Tests for the high-level api module (post_hello_world, publish_content)."""

from __future__ import annotations

import responses

from instagram_content_creator.api import (
    post_hello_world,
    post_with_location,
    publish_content,
)
from instagram_content_creator.config import InstagramConfig
from instagram_content_creator.content.post import ImagePost


@responses.activate
def test_post_hello_world_publishes_image_post_with_default_caption(
    config: InstagramConfig, set_instagram_env: None
) -> None:
    base_url = f"https://{config.host}/{config.api_version}/{config.user_id}"
    responses.add(responses.POST, f"{base_url}/media", json={"id": "container-1"}, status=200)
    responses.add(
        responses.GET,
        f"https://{config.host}/{config.api_version}/container-1",
        json={"status_code": "FINISHED"},
        status=200,
    )
    responses.add(responses.POST, f"{base_url}/media_publish", json={"id": "media-1"}, status=200)

    media_id = post_hello_world("https://example.com/img.jpg")

    assert media_id == "media-1"
    create_request = responses.calls[0].request
    assert "caption=Hello+World%21" in create_request.body


@responses.activate
def test_publish_content_with_explicit_config(config: InstagramConfig) -> None:
    base_url = f"https://{config.host}/{config.api_version}/{config.user_id}"
    responses.add(responses.POST, f"{base_url}/media", json={"id": "container-1"}, status=200)
    responses.add(
        responses.GET,
        f"https://{config.host}/{config.api_version}/container-1",
        json={"status_code": "FINISHED"},
        status=200,
    )
    responses.add(responses.POST, f"{base_url}/media_publish", json={"id": "media-1"}, status=200)

    post = ImagePost(image_url="https://example.com/img.jpg")
    media_id = publish_content(post, config=config)

    assert media_id == "media-1"
    create_request = responses.calls[0].request
    assert "caption=Hello+World%21" in create_request.body
    publish_request = responses.calls[2].request
    assert "creation_id=container-1" in publish_request.body


@responses.activate
def test_post_with_location_includes_location_id(monkeypatch) -> None:
    config = InstagramConfig(
        app_id="app-1",
        user_id="123456789",
        access_token="token-1",
        host="graph.facebook.com",
    )
    monkeypatch.setenv("INSTAGRAM_APP_ID", config.app_id)
    monkeypatch.setenv("INSTAGRAM_USER_ID", config.user_id)
    monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", config.access_token)
    monkeypatch.setenv("INSTAGRAM_API_HOST", config.host)

    base_url = f"https://{config.host}/{config.api_version}/{config.user_id}"
    responses.add(responses.POST, f"{base_url}/media", json={"id": "container-1"}, status=200)
    responses.add(
        responses.GET,
        f"https://{config.host}/{config.api_version}/container-1",
        json={"status_code": "FINISHED"},
        status=200,
    )
    responses.add(responses.POST, f"{base_url}/media_publish", json={"id": "media-1"}, status=200)

    media_id = post_with_location(
        "https://example.com/img.jpg",
        "place-123",
        caption="Ciao da Roma!",
    )

    assert media_id == "media-1"
    create_request = responses.calls[0].request
    assert "location_id=place-123" in create_request.body
    assert "caption=Ciao+da+Roma%21" in create_request.body
