"""Publishing workflow: create container(s), wait until ready, then publish them."""

from __future__ import annotations

import logging
import time
from typing import Callable

from .client import GraphAPIClient
from .content.base import ContentItem
from .exceptions import InstagramAPIError

MEDIA_PATH_TEMPLATE = "{ig_user_id}/media"
PUBLISH_PATH_TEMPLATE = "{ig_user_id}/media_publish"

FAILED_STATUSES = {"ERROR", "EXPIRED"}
DEFAULT_POLL_INTERVAL_SECONDS = 1.0
DEFAULT_MAX_POLL_ATTEMPTS = 30

logger = logging.getLogger(__name__)


class ContentPublisher:
    """Publishes any :class:`ContentItem` to an Instagram professional account."""

    def __init__(
        self,
        client: GraphAPIClient,
        ig_user_id: str,
        *,
        poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS,
        max_poll_attempts: int = DEFAULT_MAX_POLL_ATTEMPTS,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self.client = client
        self.ig_user_id = ig_user_id
        self.poll_interval_seconds = poll_interval_seconds
        self.max_poll_attempts = max_poll_attempts
        self.sleep_fn = sleep_fn

    def publish(self, content: ContentItem) -> str:
        """Create the container(s) for ``content``, wait for processing, then publish it."""
        logger.info("Publishing %s content", type(content).__name__)
        children_ids = self._create_child_containers(content)
        container_id = self._create_container(content, children_ids)
        logger.info("Media container created: %s", container_id)
        self._wait_until_ready(container_id)
        media_id = self._publish_container(container_id)
        logger.info("Media published: %s", media_id)
        return media_id

    def _create_child_containers(self, content: ContentItem) -> list[str]:
        children_ids = []
        for child_params in content.child_container_params():
            response = self.client.post(
                MEDIA_PATH_TEMPLATE.format(ig_user_id=self.ig_user_id), params=child_params
            )
            child_id = response.get("id")
            if not child_id:
                raise InstagramAPIError("Failed to create carousel child container", response=response)
            children_ids.append(child_id)
        return children_ids

    def _create_container(self, content: ContentItem, children_ids: list[str]) -> str:
        params = content.with_children(children_ids)
        response = self.client.post(
            MEDIA_PATH_TEMPLATE.format(ig_user_id=self.ig_user_id), params=params
        )
        container_id = response.get("id")
        if not container_id:
            raise InstagramAPIError("Failed to create media container", response=response)
        return container_id

    def _wait_until_ready(self, container_id: str) -> None:
        """Poll the container's status until it is FINISHED (publishable).

        Publishing right after creation can race with Meta's media processing,
        causing media_publish to fail with "Media ID is not available".
        """
        for attempt in range(self.max_poll_attempts):
            response = self.client.get(container_id, params={"fields": "status_code"})
            status = response.get("status_code")
            logger.debug(
                "Container %s status=%s (attempt %s/%s)",
                container_id, status, attempt + 1, self.max_poll_attempts,
            )
            if status in (None, "FINISHED"):
                return
            if status in FAILED_STATUSES:
                logger.error("Container %s failed to process (status=%s)", container_id, status)
                raise InstagramAPIError(
                    f"Media container failed to process (status: {status})", response=response
                )
            self.sleep_fn(self.poll_interval_seconds)
        logger.error("Timed out waiting for container %s to finish processing", container_id)
        raise InstagramAPIError("Timed out waiting for media container to finish processing")

    def _publish_container(self, container_id: str) -> str:
        response = self.client.post(
            PUBLISH_PATH_TEMPLATE.format(ig_user_id=self.ig_user_id),
            params={"creation_id": container_id},
        )
        media_id = response.get("id")
        if not media_id:
            raise InstagramAPIError("Failed to publish media container", response=response)
        return media_id
