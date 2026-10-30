"""Tests for the plain text-to-PNG image generator."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from instagram_content_creator.text_image import TextImageOptions, generate_text_image


def test_generate_text_image_creates_png_with_background_color(tmp_path: Path) -> None:
    output_path = tmp_path / "ciao.png"
    options = TextImageOptions(size=(200, 100), background_color="black", text_color="white")

    result = generate_text_image("ciao", output_path, options=options)

    assert result == output_path
    assert output_path.is_file()

    with Image.open(output_path) as image:
        assert image.size == (200, 100)
        assert image.convert("RGB").getpixel((0, 0)) == (0, 0, 0)


def test_generate_text_image_draws_text_in_the_requested_color(tmp_path: Path) -> None:
    output_path = tmp_path / "ciao.png"
    options = TextImageOptions(size=(200, 100), background_color="black", text_color="white")

    generate_text_image("ciao", output_path, options=options)

    with Image.open(output_path) as image:
        histogram = image.convert("L").histogram()
        assert histogram[255] > 0


def test_generate_text_image_rejects_empty_text(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="text must not be empty"):
        generate_text_image("   ", tmp_path / "empty.png")


def test_generate_text_image_creates_missing_parent_directories(tmp_path: Path) -> None:
    output_path = tmp_path / "nested" / "dir" / "ciao.png"

    generate_text_image("ciao", output_path)

    assert output_path.is_file()
