"""Page object for authenticated Toolshop account pages."""

from __future__ import annotations

import re

from playwright.sync_api import Locator

from src.pages.base_page import BasePage


class AccountPage(BasePage):
    """Expose profile controls after a test has authenticated independently."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.profile_heading = self.page.get_by_role("heading", level=1)
        self.profile_form = self.page.locator("form")
        self.save_button = self.page.get_by_role(
            "button", name=re.compile(r"save|update", re.IGNORECASE)
        )
        self.result_message = self.page.locator("[role='alert'], .alert")

    def open(self) -> None:
        """Open the account route for the authenticated browser context."""

        self.open_path("/account")

    def get_profile_heading(self) -> str:
        """Return the primary heading shown by the authenticated account page."""

        return self.profile_heading.inner_text()

    def profile_field(self, label: str) -> Locator:
        """Return a profile field using its accessible label."""

        return self.page.get_by_label(label, exact=True)

    def update_profile_field(self, label: str, value: str) -> None:
        """Fill one editable profile field by label."""

        self.profile_field(label).fill(value)

    def save_profile(self) -> None:
        """Save the current account profile form."""

        self.save_button.click()

    def get_result_message(self) -> str:
        """Return a currently rendered account result message."""

        return self.result_message.first.inner_text()
