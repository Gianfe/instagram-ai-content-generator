"""Tests for GraphAPIClient."""

from __future__ import annotations

import pytest
import responses

from instagram_content_creator.client import GraphAPIClient
from instagram_content_creator.config import InstagramConfig
from instagram_content_creator.exceptions import InstagramAPIError


@pytest.fixture
def client(config: InstagramConfig) -> GraphAPIClient:
    return GraphAPIClient(config)


@responses.activate
def test_post_sends_access_token_and_returns_json(client: GraphAPIClient, config: InstagramConfig) -> None:
    responses.add(
        responses.POST,
        f"https://{config.host}/{config.api_version}/123456789/media",
        json={"id": "container-1"},
        status=200,
    )

    result = client.post(f"{config.user_id}/media", params={"image_url": "https://example.com/img.jpg"})

    assert result == {"id": "container-1"}
    sent_request = responses.calls[0].request
    assert f"access_token={config.access_token}" in sent_request.body


@responses.activate
def test_get_sends_access_token_as_query_param(client: GraphAPIClient, config: InstagramConfig) -> None:
    responses.add(
        responses.GET,
        f"https://{config.host}/{config.api_version}/123456789",
        json={"id": config.user_id},
        status=200,
    )

    result = client.get(config.user_id)

    assert result == {"id": config.user_id}
    sent_request = responses.calls[0].request
    assert f"access_token={config.access_token}" in sent_request.url


@responses.activate
def test_post_raises_instagram_api_error_on_http_error(client: GraphAPIClient, config: InstagramConfig) -> None:
    responses.add(
        responses.POST,
        f"https://{config.host}/{config.api_version}/123456789/media",
        json={"error": {"message": "Invalid image URL"}},
        status=400,
    )

    with pytest.raises(InstagramAPIError, match="Invalid image URL"):
        client.post(f"{config.user_id}/media", params={"image_url": "not-a-url"})


@responses.activate
def test_post_raises_generic_error_when_body_has_no_error_message(
    client: GraphAPIClient, config: InstagramConfig
) -> None:
    responses.add(
        responses.POST,
        f"https://{config.host}/{config.api_version}/123456789/media",
        body="not json",
        status=500,
    )

    with pytest.raises(InstagramAPIError, match="status 500"):
        client.post(f"{config.user_id}/media")
