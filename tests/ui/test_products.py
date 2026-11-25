"""UI checks for Toolshop product lists and product details."""

import re

import pytest
from playwright.sync_api import Page, expect

from src.config.settings import ToolshopSettings
from src.pages.home_page import HomePage
from src.pages.product_page import ProductPage


@pytest.mark.regression
def test_product_list_available_displays_product_cards(page: Page, settings: ToolshopSettings) -> None:
    """Objective: show the catalogue. Precondition: PROD is reachable. Expected: a product card is visible."""

    home = HomePage(page, settings)
    home.open()

    expect(home.product_links.first).to_be_visible()
    expect(home.product_headings.first).to_be_visible()


@pytest.mark.regression
def test_product_detail_opened_from_list_displays_product_information(
    page: Page, settings: ToolshopSettings
) -> None:
    """Objective: open a product. Precondition: catalogue has a card. Expected: name, price and description render."""

    home = HomePage(page, settings)
    home.open()
    home.open_product()
    product = ProductPage(page, settings)

    expect(product.product_name).to_be_visible()
    expect(product.price_text.first).to_be_visible()
    expect(product.add_to_cart_button).to_be_visible()
    assert product.get_description(), "The product detail page did not provide a description."


@pytest.mark.regression
def test_product_quantity_changed_updates_accessible_quantity_control(
    page: Page, settings: ToolshopSettings
) -> None:
    """Objective: choose quantity. Precondition: a product detail is open. Expected: spinbutton shows chosen quantity."""

    home = HomePage(page, settings)
    home.open()
    home.open_product()
    product = ProductPage(page, settings)
    product.set_quantity(2)

    expect(product.quantity_input).to_have_value("2")
    expect(product.add_to_cart_button).to_be_enabled()
