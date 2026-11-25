"""UI checks for Toolshop authentication using an account created for this run."""

import re

import pytest
from playwright.sync_api import Page, expect

from src.config.settings import ToolshopSettings
from src.pages.account_page import AccountPage
from src.pages.login_page import LoginPage
from tests.conftest import RegisteredUser


@pytest.mark.regression
def test_authenticated_context_opens_account_for_registered_user(
    authenticated_page: Page, settings: ToolshopSettings
) -> None:
    """Objective: restore one authenticated context. Expected: account is accessible."""

    account = AccountPage(authenticated_page, settings)
    account.open()

    expect(authenticated_page).to_have_url(re.compile(r"/account"))
    expect(account.profile_heading).to_be_visible()


@pytest.mark.regression
def test_login_wrong_password_for_registered_user_shows_error(
    page: Page, settings: ToolshopSettings, registered_user: RegisteredUser
) -> None:
    """Objective: reject invalid credential. Precondition: private user exists. Expected: an error is rendered, not login."""

    login = LoginPage(page, settings)
    login.open()
    login.login(registered_user.email, f"{registered_user.password}wrong")

    expect(login.error_message.first).to_be_visible()
    expect(page).to_have_url(re.compile(r"/auth/login"))


@pytest.mark.regression
@pytest.mark.parametrize(
    ("email", "password", "invalid_fields"),
    [
        ("", "ValidPassword!1", ("email",)),
        ("not-an-email", "ValidPassword!1", ("email",)),
        ("qa@example.test", "", ("password",)),
    ],
    ids=["missing-email", "malformed-email", "missing-password"],
)
def test_login_invalid_input_shows_client_validation(
    page: Page,
    settings: ToolshopSettings,
    email: str,
    password: str,
    invalid_fields: tuple[str, ...],
) -> None:
    """Invalid local credentials must be rejected without touching a shared account."""

    login = LoginPage(page, settings)
    login.open()
    login.login(email, password)

    fields = {"email": login.email_input, "password": login.password_input}
    for field_name in invalid_fields:
        expect(fields[field_name]).to_have_attribute("aria-invalid", "true")
