"""Single-image feed post."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base import ContentItem

DEFAULT_CAPTION = "Hello World!"


@dataclass
class ImagePost(ContentItem):
    """A standard single-image feed post.

    The Graph API requires a publicly reachable ``image_url`` for feed posts;
    there is no way to publish a caption-only (text-only) post.
    """

    image_url: str
    caption: str = DEFAULT_CAPTION

    def container_params(self) -> dict[str, Any]:
        if not self.image_url:
            raise ValueError("image_url is required to create an image post")
        return {"image_url": self.image_url, "caption": self.caption}
