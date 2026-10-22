"""Multi-image carousel post."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import ContentItem
from .post import DEFAULT_CAPTION

MIN_CAROUSEL_ITEMS = 2
MAX_CAROUSEL_ITEMS = 10


@dataclass
class CarouselPost(ContentItem):
    """A carousel post made of 2 to 10 images.

    Each image is first created as a child container (``is_carousel_item``),
    then a parent container of ``media_type=CAROUSEL`` references them via
    ``children``.
    """

    image_urls: list[str] = field(default_factory=list)
    caption: str = DEFAULT_CAPTION

    def __post_init__(self) -> None:
        count = len(self.image_urls)
        if count < MIN_CAROUSEL_ITEMS or count > MAX_CAROUSEL_ITEMS:
            raise ValueError(
                f"A carousel requires between {MIN_CAROUSEL_ITEMS} and "
                f"{MAX_CAROUSEL_ITEMS} images, got {count}"
            )

    def child_container_params(self) -> list[dict[str, Any]]:
        return [{"image_url": url, "is_carousel_item": True} for url in self.image_urls]

    def container_params(self) -> dict[str, Any]:
        return {"caption": self.caption, "media_type": "CAROUSEL"}
