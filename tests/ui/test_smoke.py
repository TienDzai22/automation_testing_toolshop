"""Minimal browser availability checks for the configured Toolshop environment."""

import re

import pytest
from playwright.sync_api import Page, expect

from src.config.settings import ToolshopSettings


@pytest.mark.smoke
def test_toolshop_home_page_is_available(page: Page, settings: ToolshopSettings) -> None:
    """The configured Toolshop home page should load with a non-empty title."""

    response = page.goto(
        f"{settings.base_url}{settings.route_prefix}",
        wait_until="domcontentloaded",
    )

    assert response is not None, "The browser did not receive a response from Toolshop."
    assert response.ok, f"Toolshop returned HTTP {response.status}."
    expect(page).to_have_title(re.compile(r".+"))
