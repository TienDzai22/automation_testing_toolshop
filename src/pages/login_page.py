"""Page object for Toolshop authentication."""

from __future__ import annotations

from playwright.sync_api import Locator

from src.pages.base_page import BasePage


class LoginPage(BasePage):
    """Expose the supported login interactions without embedding assertions."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.email_input = self.by_test_id("email")
        self.password_input = self.by_test_id("password")
        self.submit_button = self.by_test_id("login-submit")
        self.register_link = self.by_test_id("register-link")
        self.error_message = self.page.locator("[role='alert'], .alert-danger, .invalid-feedback")

    def open(self) -> None:
        """Open the login route."""

        self.open_path("/auth/login")

    def enter_email(self, email: str) -> None:
        """Fill the email field."""

        self.email_input.fill(email)

    def enter_password(self, password: str) -> None:
        """Fill the password field."""

        self.password_input.fill(password)

    def submit(self) -> None:
        """Submit the login form."""

        self.submit_button.click()

    def login(self, email: str, password: str) -> None:
        """Fill and submit credentials for either a valid or invalid login flow."""

        self.enter_email(email)
        self.enter_password(password)
        self.submit()

    def get_error_message(self) -> str:
        """Return the current login validation or error message, if rendered."""

        return self.error_message.first.inner_text()
