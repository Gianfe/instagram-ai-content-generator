"""Upload files to Cloudinary and return their public HTTPS delivery URLs."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import cloudinary
import cloudinary.uploader
import requests
from dotenv import load_dotenv

UploadFn = Callable[..., dict[str, Any]]
GenerateFn = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class CloudinaryConfig:
    """API credentials and destination folder for Cloudinary uploads."""

    cloud_name: str
    api_key: str
    api_secret: str
    folder: str | None = None

    @classmethod
    def from_env(cls) -> CloudinaryConfig:
        """Load Cloudinary settings from environment variables or a local .env.

        Accepts either a single ``CLOUDINARY_URL`` (the format Cloudinary shows
        in its dashboard) or the three separate ``CLOUDINARY_CLOUD_NAME``,
        ``CLOUDINARY_API_KEY`` and ``CLOUDINARY_API_SECRET`` variables.
        """
        load_dotenv()

        cloudinary_url = os.getenv("CLOUDINARY_URL")
        folder = os.getenv("CLOUDINARY_FOLDER") or None

        if cloudinary_url:
            parsed = urlparse(cloudinary_url)
            if parsed.scheme != "cloudinary" or not (
                parsed.username and parsed.password and parsed.hostname
            ):
                raise OSError(
                    "CLOUDINARY_URL must match cloudinary://<api_key>:<api_secret>@<cloud_name>"
                )
            return cls(
                cloud_name=parsed.hostname,
                api_key=parsed.username,
                api_secret=parsed.password,
                folder=folder,
            )

        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")
        missing = [
            name
            for name, value in (
                ("CLOUDINARY_URL or CLOUDINARY_CLOUD_NAME", cloud_name),
                ("CLOUDINARY_API_KEY", api_key),
                ("CLOUDINARY_API_SECRET", api_secret),
            )
            if not value
        ]
        if missing:
            raise OSError(
                "Missing required environment variable(s): " + ", ".join(missing)
            )

        return cls(
            cloud_name=cloud_name,  # type: ignore[arg-type]
            api_key=api_key,  # type: ignore[arg-type]
            api_secret=api_secret,  # type: ignore[arg-type]
            folder=folder,
        )


@dataclass(frozen=True)
class CloudinaryUpload:
    """Details and public delivery URL for an uploaded Cloudinary asset."""

    public_id: str
    file_name: str
    download_url: str


class CloudinaryUploader:
    """Upload a local file to Cloudinary using configured API credentials."""

    def __init__(self, config: CloudinaryConfig, upload_fn: UploadFn | None = None) -> None:
        self.config = config
        self._upload_fn = upload_fn if upload_fn is not None else self._configured_upload_fn(config)

    @staticmethod
    def _configured_upload_fn(config: CloudinaryConfig) -> UploadFn:
        cloudinary.config(
            cloud_name=config.cloud_name,
            api_key=config.api_key,
            api_secret=config.api_secret,
            secure=True,
        )
        return cloudinary.uploader.upload

    def upload_file(self, file_path: str | Path) -> CloudinaryUpload:
        """Upload a file to Cloudinary and return its public HTTPS delivery URL."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File to upload not found: {path}")

        result = self._upload_fn(
            str(path),
            resource_type="auto",
            folder=self.config.folder,
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )

        public_id = result.get("public_id")
        if not public_id:
            raise RuntimeError("Cloudinary upload succeeded without returning a public ID")

        download_url = result.get("secure_url")
        if not download_url or not download_url.startswith("https://"):
            raise RuntimeError("Cloudinary returned a non-HTTPS download link")

        return CloudinaryUpload(
            public_id=public_id,
            file_name=path.name,
            download_url=download_url,
        )


def upload_to_cloudinary(
    file_path: str | Path,
    config: CloudinaryConfig | None = None,
) -> CloudinaryUpload:
    """Upload a file using an explicit config or Cloudinary environment settings."""
    cloudinary_config = config or CloudinaryConfig.from_env()
    return CloudinaryUploader(cloudinary_config).upload_file(file_path)


@dataclass(frozen=True)
class CloudinaryGeneratedImage:
    """Public ID and delivery URL for an AI-generated Cloudinary asset."""

    public_id: str
    download_url: str


class CloudinaryImageGenerator:
    """Generate images with Cloudinary's AI Image Generation add-on."""

    def __init__(self, config: CloudinaryConfig, generate_fn: GenerateFn | None = None) -> None:
        self.config = config
        self._generate_fn = generate_fn if generate_fn is not None else self._configured_generate_fn(config)

    @staticmethod
    def _configured_generate_fn(config: CloudinaryConfig) -> GenerateFn:
        def _generate(prompt: str, public_id: str | None) -> dict[str, Any]:
            target: dict[str, Any] = {"target_type": "managed_asset"}
            if public_id:
                target["public_id"] = public_id

            response = requests.post(
                f"https://api.cloudinary.com/v2/generate/{config.cloud_name}/text_to_image",
                auth=(config.api_key, config.api_secret),
                json={"prompt": prompt, "target": target},
                timeout=60,
            )
            response.raise_for_status()
            return response.json()

        return _generate

    def _resolve_public_id(self, public_id: str | None, folder: str | None) -> str | None:
        """Prefix public_id with the given (or configured) folder, generating a name if needed."""
        effective_folder = folder if folder is not None else self.config.folder
        if not effective_folder:
            return public_id
        name = public_id or uuid.uuid4().hex
        return f"{effective_folder.strip('/')}/{name}"

    def generate_image(
        self,
        prompt: str,
        public_id: str | None = None,
        folder: str | None = None,
    ) -> CloudinaryGeneratedImage:
        """Generate an image from a text prompt and store it as a managed Cloudinary asset."""
        if not prompt.strip():
            raise ValueError("prompt must not be empty")

        result = self._generate_fn(prompt, self._resolve_public_id(public_id, folder))

        assets = result.get("data", {}).get("assets") or []
        if not assets:
            raise RuntimeError("Cloudinary image generation returned no assets")

        storage = assets[0].get("storage", {})
        generated_public_id = storage.get("public_id")
        download_url = storage.get("secure_url")
        if not generated_public_id or not download_url:
            raise RuntimeError("Cloudinary image generation response is missing asset details")
        if not download_url.startswith("https://"):
            raise RuntimeError("Cloudinary returned a non-HTTPS download link")

        return CloudinaryGeneratedImage(public_id=generated_public_id, download_url=download_url)


def generate_image(
    prompt: str,
    public_id: str | None = None,
    folder: str | None = None,
    config: CloudinaryConfig | None = None,
) -> CloudinaryGeneratedImage:
    """Generate an image via Cloudinary AI using an explicit config or environment settings."""
    cloudinary_config = config or CloudinaryConfig.from_env()
    return CloudinaryImageGenerator(cloudinary_config).generate_image(
        prompt, public_id=public_id, folder=folder
    )
