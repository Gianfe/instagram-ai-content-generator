"""High-level, ready-to-use entry points for publishing Instagram content."""

from __future__ import annotations

from pathlib import Path

from .client import GraphAPIClient
from .cloudinary_storage import (
    CloudinaryConfig,
    CloudinaryUpload,
    upload_to_cloudinary as _upload_to_cloudinary,
)
from .config import InstagramConfig
from .content.base import ContentItem
from .content.carousel import CarouselPost
from .content.post import DEFAULT_CAPTION, ImagePost
from .publisher import ContentPublisher


def upload_to_cloudinary(
    file_path: str | Path,
    config: CloudinaryConfig | None = None,
) -> CloudinaryUpload:
    """Upload a file to Cloudinary and return its public delivery link."""
    return _upload_to_cloudinary(file_path, config=config)


def publish_content(content: ContentItem, config: InstagramConfig | None = None) -> str:
    """Publish any :class:`ContentItem` (post, story, carousel, ...) and return the media id."""
    config = config or InstagramConfig.from_env()
    client = GraphAPIClient(config)
    publisher = ContentPublisher(client, config.user_id)
    return publisher.publish(content)


def post_hello_world(image_url: str, caption: str = DEFAULT_CAPTION) -> str:
    """Publish a simple "Hello World!" image post.

    Instagram's Graph API requires a publicly reachable image for every feed
    post, so ``image_url`` must point to an image accessible over HTTPS.
    """
    return publish_content(ImagePost(image_url=image_url, caption=caption))


def post_carousel(
    image_urls: list[str],
    caption: str = DEFAULT_CAPTION,
) -> str:
    """Publish a carousel of 2 to 10 images and return its media id."""
    return publish_content(CarouselPost(image_urls=image_urls, caption=caption))
