"""Focused checks that exercise Page Object navigation without full UI coverage."""

import re

import pytest
from playwright.sync_api import Page, expect

from src.config.settings import ToolshopSettings, get_settings
from src.pages.account_page import AccountPage
from src.pages.cart_page import CartPage
from src.pages.contact_page import ContactPage
from src.pages.home_page import HomePage
from src.pages.login_page import LoginPage
from src.pages.product_page import ProductPage


@pytest.mark.regression
def test_all_page_objects_can_be_constructed(page: Page, settings: ToolshopSettings) -> None:
    """Every phase-2 page object should initialise against one browser page."""

    for page_object in (
        HomePage,
        LoginPage,
        ProductPage,
        CartPage,
        ContactPage,
        AccountPage,
    ):
        page_object(page, settings)


@pytest.mark.regression
def test_page_objects_navigate_prod(page: Page, settings: ToolshopSettings) -> None:
    """Core POMs should open real PROD routes and expose verified controls."""

    home = HomePage(page, settings)
    home.open()
    expect(home.search_input).to_be_visible()

    home.open_product()
    product = ProductPage(page, settings)
    expect(product.product_name).to_be_visible()
    expect(product.add_to_cart_button).to_be_visible()

    login = LoginPage(page, settings)
    login.open()
    expect(login.email_input).to_be_visible()
    expect(login.password_input).to_be_visible()

    contact = ContactPage(page, settings)
    contact.open()
    expect(contact.subject_select).to_be_visible()


@pytest.mark.buggy
def test_page_objects_apply_buggy_hash_route_prefix(
    page: Page, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The same POM classes should navigate BUGGY through its configured hash routes."""

    monkeypatch.setenv("TEST_ENV", "buggy")
    buggy_settings = get_settings()
    home = HomePage(page, buggy_settings)
    home.open()
    expect(home.search_input).to_be_visible()

    contact = ContactPage(page, buggy_settings)
    contact.open()
    expect(page).to_have_url(re.compile(re.escape(contact.url_for("/contact"))))
    expect(contact.email_input).to_be_visible()
