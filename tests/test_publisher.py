"""Tests for ContentPublisher."""

from __future__ import annotations

from typing import Any

import pytest

from instagram_content_creator.content.carousel import CarouselPost
from instagram_content_creator.content.post import ImagePost
from instagram_content_creator.exceptions import InstagramAPIError
from instagram_content_creator.publisher import ContentPublisher


class FakeGraphAPIClient:
    """Records calls and returns scripted responses, standing in for GraphAPIClient."""

    def __init__(self, responses_queue: list[dict[str, Any]]) -> None:
        self._responses_queue = list(responses_queue)
        self.calls: list[tuple[str, str, dict[str, Any] | None]] = []

    def post(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.calls.append(("POST", path, params))
        return self._responses_queue.pop(0)

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.calls.append(("GET", path, params))
        return self._responses_queue.pop(0)


def no_sleep(_seconds: float) -> None:
    return None


@pytest.fixture
def ig_user_id() -> str:
    return "123456789"


def make_publisher(fake_client: FakeGraphAPIClient, ig_user_id: str, **kwargs: Any) -> ContentPublisher:
    return ContentPublisher(
        client=fake_client,  # type: ignore[arg-type]
        ig_user_id=ig_user_id,
        sleep_fn=no_sleep,
        **kwargs,
    )


def test_publish_creates_container_waits_then_publishes(ig_user_id: str) -> None:
    fake_client = FakeGraphAPIClient(
        [
            {"id": "container-1"},
            {"status_code": "FINISHED"},
            {"id": "media-1"},
        ]
    )
    publisher = make_publisher(fake_client, ig_user_id)
    post = ImagePost(image_url="https://example.com/img.jpg")

    media_id = publisher.publish(post)

    assert media_id == "media-1"
    assert fake_client.calls[0] == (
        "POST",
        f"{ig_user_id}/media",
        {"image_url": "https://example.com/img.jpg", "caption": "Hello World!"},
    )
    assert fake_client.calls[1] == ("GET", "container-1", {"fields": "status_code"})
    assert fake_client.calls[2] == ("POST", f"{ig_user_id}/media_publish", {"creation_id": "container-1"})


def test_publish_polls_until_finished(ig_user_id: str) -> None:
    fake_client = FakeGraphAPIClient(
        [
            {"id": "container-1"},
            {"status_code": "IN_PROGRESS"},
            {"status_code": "IN_PROGRESS"},
            {"status_code": "FINISHED"},
            {"id": "media-1"},
        ]
    )
    publisher = make_publisher(fake_client, ig_user_id)
    post = ImagePost(image_url="https://example.com/img.jpg")

    media_id = publisher.publish(post)

    assert media_id == "media-1"
    get_calls = [call for call in fake_client.calls if call[0] == "GET"]
    assert len(get_calls) == 3


def test_publish_carousel_creates_children_before_parent(ig_user_id: str) -> None:
    fake_client = FakeGraphAPIClient(
        [
            {"id": "child-1"},
            {"id": "child-2"},
            {"id": "parent-container"},
            {"status_code": "FINISHED"},
            {"id": "media-1"},
        ]
    )
    publisher = make_publisher(fake_client, ig_user_id)
    carousel = CarouselPost(image_urls=["https://example.com/1.jpg", "https://example.com/2.jpg"])

    media_id = publisher.publish(carousel)

    assert media_id == "media-1"
    parent_call_params = fake_client.calls[2][2]
    assert parent_call_params is not None
    assert parent_call_params["children"] == "child-1,child-2"


def test_publish_raises_when_container_creation_fails(ig_user_id: str) -> None:
    fake_client = FakeGraphAPIClient([{}])
    publisher = make_publisher(fake_client, ig_user_id)
    post = ImagePost(image_url="https://example.com/img.jpg")

    with pytest.raises(InstagramAPIError, match="Failed to create media container"):
        publisher.publish(post)


def test_publish_raises_when_publish_step_fails(ig_user_id: str) -> None:
    fake_client = FakeGraphAPIClient([{"id": "container-1"}, {"status_code": "FINISHED"}, {}])
    publisher = make_publisher(fake_client, ig_user_id)
    post = ImagePost(image_url="https://example.com/img.jpg")

    with pytest.raises(InstagramAPIError, match="Failed to publish media container"):
        publisher.publish(post)


@pytest.mark.parametrize("failed_status", ["ERROR", "EXPIRED"])
def test_publish_raises_when_container_processing_fails(ig_user_id: str, failed_status: str) -> None:
    fake_client = FakeGraphAPIClient([{"id": "container-1"}, {"status_code": failed_status}])
    publisher = make_publisher(fake_client, ig_user_id)
    post = ImagePost(image_url="https://example.com/img.jpg")

    with pytest.raises(InstagramAPIError, match="failed to process"):
        publisher.publish(post)


def test_publish_raises_on_timeout_waiting_for_container(ig_user_id: str) -> None:
    fake_client = FakeGraphAPIClient([{"id": "container-1"}] + [{"status_code": "IN_PROGRESS"}] * 3)
    publisher = make_publisher(fake_client, ig_user_id, max_poll_attempts=3)
    post = ImagePost(image_url="https://example.com/img.jpg")

    with pytest.raises(InstagramAPIError, match="Timed out"):
        publisher.publish(post)
