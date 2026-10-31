"""Tests for Cloudinary uploads and AI image generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from instagram_content_creator.cloudinary_storage import (
    CloudinaryConfig,
    CloudinaryGeneratedImage,
    CloudinaryImageGenerator,
    CloudinaryUpload,
    CloudinaryUploader,
    generate_image,
    upload_to_cloudinary,
)


class _FakeUploadFn:
    def __init__(self, result: dict[str, Any]) -> None:
        self.result = result
        self.kwargs: dict[str, Any] | None = None

    def __call__(self, file_path: str, **kwargs: Any) -> dict[str, Any]:
        self.kwargs = {"file_path": file_path, **kwargs}
        return self.result


@pytest.fixture
def cloudinary_config() -> CloudinaryConfig:
    return CloudinaryConfig(
        cloud_name="demo-cloud",
        api_key="demo-key",
        api_secret="demo-secret",
        folder="instagram",
    )


def test_upload_returns_secure_download_link(
    tmp_path: Path, cloudinary_config: CloudinaryConfig
) -> None:
    file_path = tmp_path / "photo.jpg"
    file_path.write_bytes(b"image-data")
    upload_fn = _FakeUploadFn(
        {
            "public_id": "instagram/photo",
            "secure_url": "https://res.cloudinary.com/demo-cloud/image/upload/v1/instagram/photo.jpg",
        }
    )

    result = CloudinaryUploader(cloudinary_config, upload_fn=upload_fn).upload_file(file_path)

    assert result == CloudinaryUpload(
        public_id="instagram/photo",
        file_name="photo.jpg",
        download_url="https://res.cloudinary.com/demo-cloud/image/upload/v1/instagram/photo.jpg",
    )
    assert upload_fn.kwargs is not None
    assert upload_fn.kwargs["file_path"] == str(file_path)
    assert upload_fn.kwargs["folder"] == "instagram"
    assert upload_fn.kwargs["resource_type"] == "auto"


def test_upload_folder_argument_overrides_configured_folder(
    tmp_path: Path, cloudinary_config: CloudinaryConfig
) -> None:
    file_path = tmp_path / "photo.jpg"
    file_path.write_bytes(b"image-data")
    upload_fn = _FakeUploadFn(
        {
            "public_id": "other/photo",
            "secure_url": "https://res.cloudinary.com/demo-cloud/image/upload/v1/other/photo.jpg",
        }
    )

    CloudinaryUploader(cloudinary_config, upload_fn=upload_fn).upload_file(file_path, folder="other")

    assert upload_fn.kwargs is not None
    assert upload_fn.kwargs["folder"] == "other"


def test_upload_rejects_missing_local_file(cloudinary_config: CloudinaryConfig) -> None:
    upload_fn = _FakeUploadFn({})
    with pytest.raises(FileNotFoundError, match="File to upload not found"):
        CloudinaryUploader(cloudinary_config, upload_fn=upload_fn).upload_file("missing.jpg")


def test_upload_requires_public_id(
    tmp_path: Path, cloudinary_config: CloudinaryConfig
) -> None:
    file_path = tmp_path / "photo.jpg"
    file_path.write_bytes(b"image-data")
    upload_fn = _FakeUploadFn({"secure_url": "https://res.cloudinary.com/demo/image.jpg"})

    with pytest.raises(RuntimeError, match="without returning a public ID"):
        CloudinaryUploader(cloudinary_config, upload_fn=upload_fn).upload_file(file_path)


def test_upload_requires_https_secure_url(
    tmp_path: Path, cloudinary_config: CloudinaryConfig
) -> None:
    file_path = tmp_path / "photo.jpg"
    file_path.write_bytes(b"image-data")
    upload_fn = _FakeUploadFn({"public_id": "instagram/photo", "secure_url": "http://example.com"})

    with pytest.raises(RuntimeError, match="non-HTTPS download link"):
        CloudinaryUploader(cloudinary_config, upload_fn=upload_fn).upload_file(file_path)


def test_config_from_env_accepts_separate_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "instagram_content_creator.cloudinary_storage.load_dotenv",
        lambda *args, **kwargs: False,
    )
    monkeypatch.delenv("CLOUDINARY_URL", raising=False)
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "demo-cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "demo-key")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "demo-secret")
    monkeypatch.setenv("CLOUDINARY_FOLDER", "instagram")

    config = CloudinaryConfig.from_env()

    assert config == CloudinaryConfig(
        cloud_name="demo-cloud",
        api_key="demo-key",
        api_secret="demo-secret",
        folder="instagram",
    )


def test_config_from_env_accepts_cloudinary_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "instagram_content_creator.cloudinary_storage.load_dotenv",
        lambda *args, **kwargs: False,
    )
    monkeypatch.setenv("CLOUDINARY_URL", "cloudinary://demo-key:demo-secret@demo-cloud")
    monkeypatch.delenv("CLOUDINARY_FOLDER", raising=False)

    config = CloudinaryConfig.from_env()

    assert config == CloudinaryConfig(
        cloud_name="demo-cloud",
        api_key="demo-key",
        api_secret="demo-secret",
        folder=None,
    )


def test_config_from_env_reports_missing_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "instagram_content_creator.cloudinary_storage.load_dotenv",
        lambda *args, **kwargs: False,
    )
    monkeypatch.delenv("CLOUDINARY_URL", raising=False)
    monkeypatch.delenv("CLOUDINARY_CLOUD_NAME", raising=False)
    monkeypatch.delenv("CLOUDINARY_API_KEY", raising=False)
    monkeypatch.delenv("CLOUDINARY_API_SECRET", raising=False)

    with pytest.raises(OSError) as exc_info:
        CloudinaryConfig.from_env()

    assert "CLOUDINARY_CLOUD_NAME" in str(exc_info.value)
    assert "CLOUDINARY_API_KEY" in str(exc_info.value)
    assert "CLOUDINARY_API_SECRET" in str(exc_info.value)


def test_public_api_uses_environment_config(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    file_path = tmp_path / "photo.jpg"
    file_path.write_bytes(b"image-data")
    config = CloudinaryConfig("demo-cloud", "demo-key", "demo-secret")

    class _StubUploader:
        def __init__(self, received_config: CloudinaryConfig) -> None:
            assert received_config == config

        def upload_file(
            self, received_path: str | Path, folder: str | None = None
        ) -> CloudinaryUpload:
            assert received_path == file_path
            assert folder is None
            return CloudinaryUpload("instagram/photo", "photo.jpg", "https://example.com/photo")

    monkeypatch.setattr(
        "instagram_content_creator.cloudinary_storage.CloudinaryConfig.from_env",
        lambda: config,
    )
    monkeypatch.setattr(
        "instagram_content_creator.cloudinary_storage.CloudinaryUploader", _StubUploader
    )

    assert upload_to_cloudinary(file_path) == CloudinaryUpload(
        "instagram/photo", "photo.jpg", "https://example.com/photo"
    )


class _FakeGenerateFn:
    def __init__(self, result: dict[str, Any]) -> None:
        self.result = result
        self.kwargs: dict[str, Any] | None = None

    def __call__(self, prompt: str, public_id: str | None) -> dict[str, Any]:
        self.kwargs = {"prompt": prompt, "public_id": public_id}
        return self.result


class _FakeAssignFolderFn:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def __call__(self, public_id: str, folder: str) -> dict[str, Any]:
        self.calls.append((public_id, folder))
        return {}


def test_generate_image_returns_generated_asset(cloudinary_config: CloudinaryConfig) -> None:
    generate_fn = _FakeGenerateFn(
        {
            "data": {
                "assets": [
                    {
                        "storage": {
                            "public_id": "instagram/generated",
                            "secure_url": "https://res.cloudinary.com/demo-cloud/image/upload/v1/instagram/generated.png",
                        }
                    }
                ]
            }
        }
    )

    result = CloudinaryImageGenerator(
        cloudinary_config, generate_fn=generate_fn, assign_folder_fn=_FakeAssignFolderFn()
    ).generate_image("a cat wearing a cowboy hat", public_id="generated")

    assert result == CloudinaryGeneratedImage(
        public_id="instagram/generated",
        download_url="https://res.cloudinary.com/demo-cloud/image/upload/v1/instagram/generated.png",
    )
    assert generate_fn.kwargs == {
        "prompt": "a cat wearing a cowboy hat",
        "public_id": "instagram/generated",
    }


def test_generate_image_places_asset_in_configured_folder_without_explicit_name(
    cloudinary_config: CloudinaryConfig,
) -> None:
    generate_fn = _FakeGenerateFn(
        {"data": {"assets": [{"storage": {"public_id": "instagram/x", "secure_url": "https://example.com/x.png"}}]}}
    )

    CloudinaryImageGenerator(
        cloudinary_config, generate_fn=generate_fn, assign_folder_fn=_FakeAssignFolderFn()
    ).generate_image("a cat")

    assert generate_fn.kwargs is not None
    resolved_public_id = generate_fn.kwargs["public_id"]
    assert resolved_public_id.startswith("instagram/")
    assert resolved_public_id != "instagram/"


def test_generate_image_folder_argument_overrides_configured_folder(
    cloudinary_config: CloudinaryConfig,
) -> None:
    generate_fn = _FakeGenerateFn(
        {"data": {"assets": [{"storage": {"public_id": "other/cat", "secure_url": "https://example.com/cat.png"}}]}}
    )

    CloudinaryImageGenerator(
        cloudinary_config, generate_fn=generate_fn, assign_folder_fn=_FakeAssignFolderFn()
    ).generate_image("a cat", public_id="cat", folder="other")

    assert generate_fn.kwargs == {"prompt": "a cat", "public_id": "other/cat"}


def test_generate_image_assigns_asset_folder_when_folder_is_set(
    cloudinary_config: CloudinaryConfig,
) -> None:
    generate_fn = _FakeGenerateFn(
        {"data": {"assets": [{"storage": {"public_id": "instagram/cat", "secure_url": "https://example.com/cat.png"}}]}}
    )
    assign_folder_fn = _FakeAssignFolderFn()

    CloudinaryImageGenerator(
        cloudinary_config, generate_fn=generate_fn, assign_folder_fn=assign_folder_fn
    ).generate_image("a cat", public_id="cat")

    assert assign_folder_fn.calls == [("instagram/cat", "instagram")]


def test_generate_image_without_folder_leaves_public_id_untouched() -> None:
    config = CloudinaryConfig("demo-cloud", "demo-key", "demo-secret", folder=None)
    generate_fn = _FakeGenerateFn(
        {"data": {"assets": [{"storage": {"public_id": "generated", "secure_url": "https://example.com/x.png"}}]}}
    )

    CloudinaryImageGenerator(config, generate_fn=generate_fn).generate_image("a cat", public_id="generated")

    assert generate_fn.kwargs == {"prompt": "a cat", "public_id": "generated"}


def test_generate_image_rejects_empty_prompt(cloudinary_config: CloudinaryConfig) -> None:
    with pytest.raises(ValueError, match="prompt must not be empty"):
        CloudinaryImageGenerator(cloudinary_config, generate_fn=_FakeGenerateFn({})).generate_image("   ")


def test_generate_image_requires_assets_in_response(cloudinary_config: CloudinaryConfig) -> None:
    generate_fn = _FakeGenerateFn({"data": {"assets": []}})

    with pytest.raises(RuntimeError, match="returned no assets"):
        CloudinaryImageGenerator(cloudinary_config, generate_fn=generate_fn).generate_image("a cat")


def test_generate_image_requires_https_secure_url(cloudinary_config: CloudinaryConfig) -> None:
    generate_fn = _FakeGenerateFn(
        {"data": {"assets": [{"storage": {"public_id": "x", "secure_url": "http://example.com"}}]}}
    )

    with pytest.raises(RuntimeError, match="non-HTTPS download link"):
        CloudinaryImageGenerator(cloudinary_config, generate_fn=generate_fn).generate_image("a cat")


def test_generate_image_public_api_uses_environment_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = CloudinaryConfig("demo-cloud", "demo-key", "demo-secret")

    class _StubGenerator:
        def __init__(self, received_config: CloudinaryConfig) -> None:
            assert received_config == config

        def generate_image(
            self, prompt: str, public_id: str | None = None, folder: str | None = None
        ) -> CloudinaryGeneratedImage:
            assert prompt == "a cat"
            assert public_id == "instagram/cat"
            assert folder is None
            return CloudinaryGeneratedImage("instagram/cat", "https://example.com/cat")

    monkeypatch.setattr(
        "instagram_content_creator.cloudinary_storage.CloudinaryConfig.from_env",
        lambda: config,
    )
    monkeypatch.setattr(
        "instagram_content_creator.cloudinary_storage.CloudinaryImageGenerator", _StubGenerator
    )

    assert generate_image("a cat", public_id="instagram/cat") == CloudinaryGeneratedImage(
        "instagram/cat", "https://example.com/cat"
    )
