"""Pytest fixtures shared by UI, API, and BDD tests."""

from __future__ import annotations

import secrets
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import pytest
from playwright.sync_api import APIRequestContext, Browser, Page, Playwright, expect

from src.config.settings import ToolshopSettings, get_settings


@dataclass(frozen=True)
class RegisteredUser:
    """Credentials for an isolated account created specifically for this test run."""

    email: str
    password: str


@dataclass(frozen=True)
class AuthenticatedStorageState:
    """Worker-private persisted authentication plus any captured session storage."""

    path: Path
    session_storage: dict[str, str]


@pytest.fixture(scope="session", autouse=True)
def configure_playwright_selectors(playwright: Playwright) -> None:
    """Use Toolshop's stable ``data-test`` convention for future POM locators."""

    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture(scope="session")
def settings() -> ToolshopSettings:
    """Provide the selected Toolshop environment configuration once per run."""

    return get_settings()


@pytest.fixture
def api_context(
    playwright: Playwright, settings: ToolshopSettings
) -> Iterator[APIRequestContext]:
    """Provide one disposable Playwright API client for an isolated test."""

    request = playwright.request.new_context(base_url=settings.api_url)
    try:
        yield request
    finally:
        request.dispose()


@pytest.fixture(scope="session")
def registered_user(playwright: Playwright, settings: ToolshopSettings) -> RegisteredUser:
    """Register one random customer using the request format of the selected API."""

    token = secrets.token_hex(8)
    user = RegisteredUser(
        email=f"ui.{token}@example.test",
        password=f"Qa!{secrets.token_urlsafe(14)}9",
    )
    registration_data = {
        "first_name": "UI",
        "last_name": "Automation",
        "email": user.email,
        "password": user.password,
        "phone": "0900000000",
        "dob": "1990-01-01",
    }
    if settings.environment == "buggy":
        registration_data.update(
            {
                "address": "Automation Street 3",
                "city": "Test City",
                "state": "QA",
                "country": "Vietnam",
                "postcode": "700000",
            }
        )
    else:
        registration_data["address"] = {
            "street": "Automation Street",
            "house_number": "3",
            "city": "Test City",
            "state": "QA",
            "country": "Vietnam",
            "postal_code": "700000",
        }

    request: APIRequestContext = playwright.request.new_context(base_url=settings.api_url)
    response = request.post(
        "/users/register",
        data=registration_data,
    )
    assert response.status == 201, (
        f"Could not create isolated test account: HTTP {response.status} {response.text()}"
    )
    request.dispose()
    return user


def _worker_id(request: pytest.FixtureRequest) -> str:
    """Return a stable xdist worker name, or a useful name outside xdist."""

    worker_input = getattr(request.config, "workerinput", None)
    return worker_input.get("workerid", "master") if worker_input else "master"


@pytest.fixture(scope="session")
def authenticated_storage_state(
    browser: Browser,
    registered_user: RegisteredUser,
    request: pytest.FixtureRequest,
    settings: ToolshopSettings,
    tmp_path_factory: pytest.TempPathFactory,
) -> AuthenticatedStorageState:
    """Log in once per worker and persist the resulting browser storage state.

    Playwright persists cookies and local storage in ``storage_state``.  The buggy
    deployment uses session storage, which Playwright intentionally does not put
    in that file, so its key/value pairs are captured separately and restored by
    ``authenticated_page`` before a document is created.
    """

    worker_id = _worker_id(request)
    state_dir = tmp_path_factory.mktemp(f"auth-state-{worker_id}")
    state_path = state_dir / "storage-state.json"
    context = browser.new_context()
    page = context.new_page()
    try:
        from src.pages.login_page import LoginPage

        login = LoginPage(page, settings)
        login.open()
        login.login(registered_user.email, registered_user.password)
        expect(page).to_have_url(re.compile(r"/account"))
        session_storage = page.evaluate(
            "Object.fromEntries(Object.entries(sessionStorage))"
        )
        context.storage_state(path=state_path)
    finally:
        context.close()

    assert state_path.is_file(), "Authenticated storage state was not written."
    return AuthenticatedStorageState(path=state_path, session_storage=session_storage)


@pytest.fixture
def authenticated_page(
    browser: Browser,
    authenticated_storage_state: AuthenticatedStorageState,
    settings: ToolshopSettings,
) -> Iterator[Page]:
    """Give one test an isolated page authenticated from worker-private state."""

    context = browser.new_context(storage_state=str(authenticated_storage_state.path))
    if settings.environment == "buggy" and authenticated_storage_state.session_storage:
        context.add_init_script(
            """entries => {
                for (const [key, value] of Object.entries(entries)) {
                    sessionStorage.setItem(key, value);
                }
            }""",
            authenticated_storage_state.session_storage,
        )
    page = context.new_page()
    try:
        yield page
    finally:
        context.close()


@pytest.fixture
def cleanup_cart(page, playwright: Playwright, settings: ToolshopSettings):
    """Remove the anonymous cart created by one UI test after that test completes."""

    yield
    if not page.url.startswith(("http://", "https://")):
        return
    cart_id = page.evaluate("sessionStorage.getItem('cart_id')")
    if not cart_id:
        return

    request: APIRequestContext = playwright.request.new_context(base_url=settings.api_url)
    response = request.delete(f"/carts/{cart_id}")
    assert response.status in {204, 404}, (
        f"Could not clean up test cart {cart_id}: HTTP {response.status}"
    )
    request.dispose()
