"""UI checks for Toolshop's anonymous cart and checkout step."""

import re
from decimal import Decimal, ROUND_HALF_UP

import pytest
from playwright.sync_api import Page, expect

from src.config.settings import ToolshopSettings
from src.pages.cart_page import CartPage
from src.pages.home_page import HomePage
from src.pages.product_page import ProductPage


def _add_first_product(page: Page, settings: ToolshopSettings) -> tuple[CartPage, Decimal]:
    """Add a dynamically discovered product and return its cart page object."""

    home = HomePage(page, settings)
    home.open()
    home.open_product()
    product = ProductPage(page, settings)
    unit_price = _money(product.get_price())
    product.add_to_cart()
    return CartPage(page, settings), unit_price


def _money(value: str) -> Decimal:
    """Parse a UI currency amount into a two-decimal value for cart assertions."""

    match = re.search(r"(\d+(?:\.\d{1,2})?)", value.replace(",", ""))
    assert match, f"No monetary amount found in {value!r}."
    return Decimal(match.group(1)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _open_cart(page: Page, cart: CartPage) -> None:
    """Open checkout and wait for the cart data request that renders its line items."""

    with page.expect_response(
        lambda response: "/carts/" in response.url and response.request.method == "GET"
    ) as response_info:
        cart.open()
    assert response_info.value.status == 200


@pytest.mark.regression
def test_cart_add_product_exposes_checkout_cart_link(
    page: Page, settings: ToolshopSettings, cleanup_cart
) -> None:
    """Objective: add to cart. Precondition: product is available. Expected: cart link shows one selected item."""

    cart, _ = _add_first_product(page, settings)

    expect(cart.cart_link).to_be_visible()
    expect(cart.cart_link).to_contain_text("1")


@pytest.mark.regression
def test_cart_quantity_changed_updates_checkout_line_quantity(
    page: Page, settings: ToolshopSettings, cleanup_cart
) -> None:
    """Objective: update cart quantity. Precondition: anonymous cart has one item. Expected: checkout input shows two."""

    cart, unit_price = _add_first_product(page, settings)
    expect(cart.cart_link).to_be_visible()
    _open_cart(page, cart)
    expect(cart.product_titles.first).to_be_visible()
    total_before = _money(cart.get_total())

    expected_total = (unit_price * 2).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    with page.expect_response(
        lambda response: "/carts/" in response.url
        and response.request.method in {"PATCH", "PUT"}
    ) as response_info:
        cart.set_quantity(item_index=0, quantity=2)
    assert response_info.value.status in {200, 204}
    expect(cart.quantity_inputs.first).to_have_value("2")
    expect(cart.total_text).to_contain_text(f"{expected_total:.2f}")
    total_after = _money(cart.get_total())

    assert total_before == unit_price, (
        f"Initial cart total {total_before} did not match unit price {unit_price}."
    )
    assert total_after == expected_total, (
        f"Quantity 2 should total {unit_price * 2}, but UI rendered {total_after}."
    )


@pytest.mark.regression
def test_cart_remove_product_control_is_available_for_cart_item(
    page: Page, settings: ToolshopSettings, cleanup_cart
) -> None:
    """Objective: remove an item. Precondition: anonymous cart has one item. Expected: a usable remove control is shown."""

    cart, _ = _add_first_product(page, settings)
    expect(cart.cart_link).to_be_visible()
    _open_cart(page, cart)

    expect(cart.remove_buttons.first).to_be_visible()
    cart.remove_item(item_index=0)
    expect(cart.product_titles).to_have_count(0)
