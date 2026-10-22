"""Single-image story."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base import ContentItem


@dataclass
class ImageStory(ContentItem):
    """A single-image story, published to the account's Stories tray."""

    image_url: str

    def container_params(self) -> dict[str, Any]:
        if not self.image_url:
            raise ValueError("image_url is required to create a story")
        return {"image_url": self.image_url, "media_type": "STORIES"}
