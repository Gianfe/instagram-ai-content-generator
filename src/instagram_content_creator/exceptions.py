"""Custom exceptions for the Instagram Content Creator package."""

from __future__ import annotations

from typing import Any


class InstagramAPIError(Exception):
    """Raised when the Instagram Graph API returns an error or unexpected response."""

    def __init__(self, message: str, response: Any = None) -> None:
        super().__init__(message)
        self.response = response
