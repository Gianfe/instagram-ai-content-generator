"""Render plain text onto a solid-color PNG, with no AI involved."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TextImageOptions:
    """Visual settings for a generated text image."""

    size: tuple[int, int] = (1080, 1080)
    background_color: str = "black"
    text_color: str = "white"
    font_path: str | None = None
    font_size: int = 80


def _load_font(options: TextImageOptions) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load the requested TrueType font, falling back to Pillow's bundled default font."""
    for candidate in filter(None, [options.font_path, "arial.ttf"]):
        try:
            return ImageFont.truetype(candidate, options.font_size)
        except OSError:
            continue
    return ImageFont.load_default(size=options.font_size)


def generate_text_image(
    text: str,
    output_path: str | Path,
    options: TextImageOptions | None = None,
) -> Path:
    """Render ``text`` centered on a solid-color background and save it as a PNG."""
    if not text.strip():
        raise ValueError("text must not be empty")

    options = options or TextImageOptions()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGB", options.size, color=options.background_color)
    draw = ImageDraw.Draw(image)
    font = _load_font(options)

    bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((options.size[0] - text_width) / 2, (options.size[1] - text_height) / 2)

    draw.multiline_text(position, text, fill=options.text_color, font=font, align="center")
    image.save(path, "PNG")
    logger.info("Generated text image at %s (size=%s)", path, options.size)
    return path
