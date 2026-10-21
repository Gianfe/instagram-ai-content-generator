from __future__ import annotations

import argparse
import json

from .client import create_default_client


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish a sample image post to Instagram via the Graph API.")
    parser.add_argument("--caption", default="Hello from Codespaces!", help="Text to publish as the Instagram caption.")
    parser.add_argument("--image-url", default=None, help="Optional public image URL to use instead of the default placeholder.")
    args = parser.parse_args()

    client = create_default_client()
    response = client.create_post(args.caption, args.image_url)
    print(json.dumps(response, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
