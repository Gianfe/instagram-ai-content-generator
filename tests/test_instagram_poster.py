from __future__ import annotations

import argparse

from .client import create_default_client


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish a test post to Instagram via the Graph API")
    parser.add_argument("--caption", default="Hello word", help="Caption to publish with the post")
    parser.add_argument(
        "--image-url",
        default=None,
        help="Publicly accessible image URL used for the post. If omitted, a placeholder image is used.",
    )
    args = parser.parse_args()

    client = create_default_client()
    result = client.create_post(caption=args.caption, image_url=args.image_url)
    print(result)


if __name__ == "__main__":
    main()
