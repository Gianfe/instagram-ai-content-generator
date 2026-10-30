"""Command-line entry point: python -m instagram_content_creator --image-url <url>."""

from __future__ import annotations

import argparse
import logging

from .api import post_hello_world
from .content.post import DEFAULT_CAPTION
from .exceptions import InstagramAPIError

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    parser = argparse.ArgumentParser(description="Publish a Hello World post to Instagram.")
    parser.add_argument("--image-url", required=True, help="Publicly reachable HTTPS image URL")
    parser.add_argument("--caption", default=DEFAULT_CAPTION, help="Post caption")
    args = parser.parse_args(argv)

    try:
        media_id = post_hello_world(image_url=args.image_url, caption=args.caption)
    except (OSError, InstagramAPIError) as exc:
        logger.error("Error: %s", exc)
        return 1

    logger.info("Published media id: %s", media_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
