"""pytest-bdd step definitions for the anonymous shopping journey."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from playwright.sync_api import Page, Response, expect
from pytest_bdd import given, parsers, scenarios, then, when

from src.config.settings import ToolshopSettings
from src.pages.cart_page import CartPage
from src.pages.home_page import HomePage
from src.pages.product_page import ProductPage


pytestmark = pytest.mark.bdd

scenarios("../features/shopping.feature")


@dataclass
class ShoppingState:
    """Keep scenario data while all UI interactions remain in page objects."""

    home: HomePage | None = None
    product: ProductPage | None = None
    cart: CartPage | None = None
    selected_product_name: str = ""


@pytest.fixture
def shopping_state() -> ShoppingState:
    """Give every Scenario Outline example an independent journey state."""

    return ShoppingState()


def _search_response_matches(response: Response, settings: ToolshopSettings, query: str) -> bool:
    """Identify the current catalogue response produced by one search action."""

    return response.url.startswith(f"{settings.api_url}/products") and (
        query.casefold() in response.url.casefold()
        or query.casefold() in (response.request.post_data or "").casefold()
    )


def _first_response_product_name(payload: object) -> str:
    """Read the first product name from Toolshop's documented list envelope."""

    assert isinstance(payload, dict), payload
    products = payload.get("data")
    assert isinstance(products, list) and products, payload
    first_product = products[0]
    assert isinstance(first_product, dict), first_product
    name = first_product.get("name")
    assert isinstance(name, str) and name, first_product
    return name


@given("the customer views the product catalogue")
def customer_views_catalogue(
    page: Page,
    settings: ToolshopSettings,
    shopping_state: ShoppingState,
    cleanup_cart,
) -> None:
    """Open the catalogue and initialise cart cleanup for this scenario."""

    del cleanup_cart
    shopping_state.home = HomePage(page, settings)
    shopping_state.home.open()
    expect(shopping_state.home.product_headings.first).to_be_visible()


@when(parsers.parse('they search for "{query}"'))
def customer_searches_for_product(
    page: Page,
    settings: ToolshopSettings,
    query: str,
    shopping_state: ShoppingState,
) -> None:
    """Search through the catalogue POM and prove matching cards are rendered."""

    assert shopping_state.home is not None, "The catalogue was not opened."
    with page.expect_response(
        lambda response: _search_response_matches(response, settings, query)
    ) as response_info:
        shopping_state.home.search(query)
    response = response_info.value
    assert response.status == 200
    first_name = _first_response_product_name(response.json())
    expect(shopping_state.home.product_headings.first).to_have_text(first_name)
    names = shopping_state.home.get_product_names()
    assert names and all(query.casefold() in name.casefold() for name in names), names


@when("they open a matching product")
def customer_opens_matching_product(
    page: Page, settings: ToolshopSettings, shopping_state: ShoppingState
) -> None:
    """Open the first current search result without relying on a product id."""

    assert shopping_state.home is not None, "No search results are available."
    shopping_state.selected_product_name = shopping_state.home.get_first_product_name().strip()
    shopping_state.home.open_product()
    shopping_state.product = ProductPage(page, settings)
    expect(shopping_state.product.product_name).to_have_text(shopping_state.selected_product_name)


@when("they add the selected product to the cart")
def customer_adds_product_to_cart(
    page: Page, settings: ToolshopSettings, shopping_state: ShoppingState
) -> None:
    """Add the selected detail item using the product and cart page objects."""

    assert shopping_state.product is not None, "No product detail is open."
    shopping_state.product.add_to_cart()
    shopping_state.cart = CartPage(page, settings)
    expect(shopping_state.cart.cart_link).to_be_visible()


@then("the cart shows the selected product")
def cart_shows_selected_product(shopping_state: ShoppingState) -> None:
    """Open the cart and verify its rendered line matches the selected product."""

    assert shopping_state.cart is not None, "The cart was not created."
    shopping_state.cart.open()
    expect(shopping_state.cart.product_titles.first).to_be_visible()
    expect(shopping_state.cart.product_titles.first).to_contain_text(
        shopping_state.selected_product_name
    )
