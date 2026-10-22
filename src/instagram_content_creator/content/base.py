"""Abstract base class for publishable Instagram content types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ContentItem(ABC):
    """Base class every publishable content type (post, story, carousel...) must implement.

    The publishing flow for the Instagram Graph API is always a two-step process:
    1. Create a media container with ``container_params()``.
    2. Publish that container.

    Content types made of multiple media items (e.g. carousels) can override
    ``child_container_params()`` to describe child containers that must be
    created first; their ids are then injected into ``container_params()``
    automatically by the publisher via ``with_children()``.
    """

    @abstractmethod
    def container_params(self) -> dict[str, Any]:
        """Parameters used to create the (parent) media container."""
        raise NotImplementedError

    def child_container_params(self) -> list[dict[str, Any]]:
        """Parameters for child media containers, created before the parent one.

        Returns an empty list by default; override for multi-item content
        types such as carousels.
        """
        return []

    def with_children(self, children_ids: list[str]) -> dict[str, Any]:
        """Merge created child container ids into the parent container params."""
        params = self.container_params()
        if children_ids:
            params["children"] = ",".join(children_ids)
        return params
