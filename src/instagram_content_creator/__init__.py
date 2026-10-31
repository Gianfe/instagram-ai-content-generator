"""Instagram Content Creator.

A small, extensible client for publishing content to an Instagram
professional account via the Meta Graph API.

Currently supported:
    - Image posts (feed)

Planned extensions (see ``instagram_content_creator.content``):
    - Stories
    - Carousels
    - Reels / video posts
"""

from .api import (
    post_carousel,
    post_hello_world,
    publish_content,
    upload_to_cloudinary,
)
from .cloudinary_storage import CloudinaryConfig, CloudinaryUpload
from .config import InstagramConfig
from .exceptions import InstagramAPIError
from .text_image import TextImageOptions, generate_text_image

__all__ = [
    "post_hello_world",
    "post_carousel",
    "publish_content",
    "upload_to_cloudinary",
    "CloudinaryConfig",
    "CloudinaryUpload",
    "InstagramConfig",
    "InstagramAPIError",
    "TextImageOptions",
    "generate_text_image",
]

__version__ = "0.1.0"
