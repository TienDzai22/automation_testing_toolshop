"""Centralised environment settings for Toolshop test runs."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class ToolshopSettings:
    """URLs and route conventions for one Toolshop test environment."""

    base_url: str
    api_url: str
    route_prefix: str
    environment: str


def _normalise_url(value: str) -> str:
    return value.rstrip("/")


def get_settings() -> ToolshopSettings:
    """Read Toolshop endpoints from environment variables.

    Defaults point to PROD so a fresh clone can run the initial smoke test.
    Every value can be overridden by CI or a local PowerShell session.
    """

    environment = os.getenv("TEST_ENV", "prod").strip().lower()
    if environment not in {"prod", "buggy"}:
        raise ValueError("TEST_ENV must be either 'prod' or 'buggy'.")

    is_buggy = environment == "buggy"
    default_base_url = (
        "https://with-bugs.practicesoftwaretesting.com"
        if is_buggy
        else "https://practicesoftwaretesting.com"
    )
    default_api_url = (
        "https://api-with-bugs.practicesoftwaretesting.com"
        if is_buggy
        else "https://api.practicesoftwaretesting.com"
    )
    default_route_prefix = "/#" if is_buggy else ""

    return ToolshopSettings(
        base_url=_normalise_url(os.getenv("BASE_URL", default_base_url)),
        api_url=_normalise_url(os.getenv("API_URL", default_api_url)),
        route_prefix=os.getenv("ROUTE_PREFIX", default_route_prefix).rstrip("/"),
        environment=environment,
    )
