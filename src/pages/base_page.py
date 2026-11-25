"""Shared browser interactions for Toolshop page objects."""

from __future__ import annotations

from playwright.sync_api import Locator, Page, Response

from src.config.settings import ToolshopSettings


class BasePage:
    """Base class that resolves application routes for either environment."""

    def __init__(self, page: Page, settings: ToolshopSettings) -> None:
        self.page = page
        self.settings = settings

    def url_for(self, path: str = "/") -> str:
        """Return an application URL that respects the configured route prefix."""

        normalised_path = "" if path in {"", "/"} else f"/{path.lstrip('/')}"
        route_prefix = self.settings.route_prefix.rstrip("/")
        return f"{self.settings.base_url}{route_prefix}{normalised_path}"

    def open_path(self, path: str = "/") -> Response | None:
        """Navigate to an application path and wait until its DOM is available."""

        return self.page.goto(self.url_for(path), wait_until="domcontentloaded")

    def by_test_id(self, value: str) -> Locator:
        """Return a locator using Toolshop's configured ``data-test`` attribute."""

        return self.page.get_by_test_id(value)

    def click_navigation(self, navigation_test_id: str) -> None:
        """Use a stable navigation test id, such as ``nav-contact``."""

        self.by_test_id(navigation_test_id).click()

    @property
    def github_footer_link(self) -> Locator:
        """Return the common footer link that opens Toolshop's GitHub project."""

        return self.by_test_id("footer-learn-github")
