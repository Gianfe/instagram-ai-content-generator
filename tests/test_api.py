"""Tests for the high-level api module (post_hello_world, publish_content)."""

from __future__ import annotations

from pathlib import Path

import pytest
import responses

from instagram_content_creator.api import (
    post_carousel,
    post_hello_world,
    publish_content,
    upload_to_cloudinary,
)
from instagram_content_creator.cloudinary_storage import (
    CloudinaryConfig,
    CloudinaryUpload,
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
def test_post_carousel_publishes_images_with_caption(
    config: InstagramConfig, set_instagram_env: None
) -> None:
    base_url = f"https://{config.host}/{config.api_version}/{config.user_id}"
    responses.add(responses.POST, f"{base_url}/media", json={"id": "child-1"}, status=200)
    responses.add(responses.POST, f"{base_url}/media", json={"id": "child-2"}, status=200)
    responses.add(responses.POST, f"{base_url}/media", json={"id": "container-1"}, status=200)
    responses.add(
        responses.GET,
        f"https://{config.host}/{config.api_version}/container-1",
        json={"status_code": "FINISHED"},
        status=200,
    )
    responses.add(responses.POST, f"{base_url}/media_publish", json={"id": "media-1"}, status=200)

    media_id = post_carousel(
        ["https://example.com/1.jpg", "https://example.com/2.jpg"],
        caption="Il mio carosello",
    )

    assert media_id == "media-1"
    assert "is_carousel_item=True" in responses.calls[0].request.body
    assert "is_carousel_item=True" in responses.calls[1].request.body
    parent_request = responses.calls[2].request
    assert "media_type=CAROUSEL" in parent_request.body
    assert "children=child-1%2Cchild-2" in parent_request.body
    assert "caption=Il+mio+carosello" in parent_request.body


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


def test_upload_to_cloudinary_delegates_to_cloudinary_uploader(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    config = CloudinaryConfig("demo-cloud", "demo-key", "demo-secret")
    expected = CloudinaryUpload(
        public_id="instagram/image",
        file_name="image.jpg",
        download_url="https://res.cloudinary.com/demo-cloud/image/upload/v1/image.jpg",
    )
    received: dict[str, object] = {}

    def fake_upload(
        file_path: str | Path,
        folder: str | None = None,
        config: CloudinaryConfig | None = None,
    ) -> CloudinaryUpload:
        received["file_path"] = file_path
        received["folder"] = folder
        received["config"] = config
        return expected

    monkeypatch.setattr(
        "instagram_content_creator.api._upload_to_cloudinary", fake_upload
    )

    result = upload_to_cloudinary("image.jpg", folder="instagram", config=config)

    assert result == expected
    assert received == {"file_path": "image.jpg", "folder": "instagram", "config": config}
