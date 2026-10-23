"""Tests for content types (ImagePost, ImageStory, CarouselPost)."""

from __future__ import annotations

import pytest

from instagram_content_creator.content.carousel import CarouselPost
from instagram_content_creator.content.post import ImagePost
from instagram_content_creator.content.story import ImageStory


class TestImagePost:
    def test_container_params_defaults_caption_to_hello_world(self) -> None:
        post = ImagePost(image_url="https://example.com/img.jpg")

        assert post.container_params() == {
            "image_url": "https://example.com/img.jpg",
            "caption": "Hello World!",
        }

    def test_container_params_with_custom_caption(self) -> None:
        post = ImagePost(image_url="https://example.com/img.jpg", caption="Custom caption")

        assert post.container_params()["caption"] == "Custom caption"

    def test_container_params_with_location_id(self) -> None:
        post = ImagePost(
            image_url="https://example.com/img.jpg",
            location_id="123456789",
        )

        assert post.container_params() == {
            "image_url": "https://example.com/img.jpg",
            "caption": "Hello World!",
            "location_id": "123456789",
        }

    def test_requires_image_url(self) -> None:
        post = ImagePost(image_url="")

        with pytest.raises(ValueError, match="image_url"):
            post.container_params()

    def test_rejects_empty_location_id(self) -> None:
        post = ImagePost(image_url="https://example.com/img.jpg", location_id="")

        with pytest.raises(ValueError, match="location_id"):
            post.container_params()

    def test_has_no_child_containers(self) -> None:
        post = ImagePost(image_url="https://example.com/img.jpg")

        assert post.child_container_params() == []


class TestImageStory:
    def test_container_params_sets_stories_media_type(self) -> None:
        story = ImageStory(image_url="https://example.com/story.jpg")

        assert story.container_params() == {
            "image_url": "https://example.com/story.jpg",
            "media_type": "STORIES",
        }

    def test_requires_image_url(self) -> None:
        story = ImageStory(image_url="")

        with pytest.raises(ValueError, match="image_url"):
            story.container_params()


class TestCarouselPost:
    def test_builds_child_params_for_each_image(self) -> None:
        carousel = CarouselPost(image_urls=["https://example.com/1.jpg", "https://example.com/2.jpg"])

        assert carousel.child_container_params() == [
            {"image_url": "https://example.com/1.jpg", "is_carousel_item": True},
            {"image_url": "https://example.com/2.jpg", "is_carousel_item": True},
        ]

    def test_container_params_sets_carousel_media_type(self) -> None:
        carousel = CarouselPost(
            image_urls=["https://example.com/1.jpg", "https://example.com/2.jpg"],
            caption="My carousel",
        )

        assert carousel.container_params() == {"caption": "My carousel", "media_type": "CAROUSEL"}

    def test_with_children_merges_ids_into_params(self) -> None:
        carousel = CarouselPost(image_urls=["https://example.com/1.jpg", "https://example.com/2.jpg"])

        params = carousel.with_children(["child-1", "child-2"])

        assert params["children"] == "child-1,child-2"

    @pytest.mark.parametrize("image_count", [0, 1, 11])
    def test_rejects_invalid_item_counts(self, image_count: int) -> None:
        image_urls = [f"https://example.com/{i}.jpg" for i in range(image_count)]

        with pytest.raises(ValueError, match="between 2 and 10"):
            CarouselPost(image_urls=image_urls)
