"""High-level, ready-to-use entry points for publishing Instagram content."""

from __future__ import annotations

from .client import GraphAPIClient
from .config import InstagramConfig
from .content.base import ContentItem
from .content.post import DEFAULT_CAPTION, ImagePost
from .publisher import ContentPublisher


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
