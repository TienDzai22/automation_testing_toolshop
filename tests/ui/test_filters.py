"""UI checks for Toolshop category, sorting, and price filters."""

from decimal import Decimal

import pytest
from playwright.sync_api import Page, expect

from src.config.settings import ToolshopSettings
from src.pages.home_page import HomePage


def _products_from_response(payload: object) -> list[dict[str, object]]:
    """Normalise Toolshop's paginated products response without assuming ids."""

    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        products = payload.get("data", payload.get("products", []))
        if isinstance(products, list):
            return [item for item in products if isinstance(item, dict)]
    raise AssertionError(f"Unexpected products response shape: {payload!r}")


def _product_category_id(product: dict[str, object]) -> str | None:
    """Return the category id represented by either supported API shape."""

    direct_id = product.get("category_id")
    if direct_id is not None:
        return str(direct_id)
    category = product.get("category")
    if isinstance(category, dict) and category.get("id") is not None:
        return str(category["id"])
    if category is not None:
        return str(category)
    return None


@pytest.mark.regression
def test_category_filter_selects_an_available_category(page: Page, settings: ToolshopSettings) -> None:
    """Objective: filter catalogue. Precondition: category filters exist. Expected: selected filter and results are visible."""

    home = HomePage(page, settings)
    home.open()
    expect(home.product_links.first).to_be_visible(timeout=15_000)
    category_filter = home.leaf_category_filters.first
    selected_category_id = category_filter.get_attribute("value")
    assert selected_category_id, "The selected category checkbox has no category value."
    with page.expect_response(
        lambda response: response.url == f"{settings.api_url}/products"
        and response.request.method == "QUERY"
    ) as response_info:
        category_filter.check()

    expect(category_filter).to_be_checked()
    expect(home.product_links.first).to_be_visible()
    response = response_info.value
    assert response.status == 200
    products = _products_from_response(response.json())
    assert products, "The category filter response contained no products."
    category_ids = [_product_category_id(product) for product in products]
    assert all(category_id == selected_category_id for category_id in category_ids), (
        f"Category {selected_category_id} rendered products from categories {category_ids}."
    )


@pytest.mark.regression
def test_sort_price_low_to_high_orders_displayed_product_prices(
    page: Page, settings: ToolshopSettings
) -> None:
    """Objective: sort by price. Precondition: products are listed. Expected: rendered prices are ascending."""

    home = HomePage(page, settings)
    home.open()
    expect(home.product_links.first).to_be_visible()
    with page.expect_response(
        lambda response: response.url == f"{settings.api_url}/products"
        and response.request.method == "QUERY"
    ) as response_info:
        home.select_sort("Price (Low - High)")
    response = response_info.value
    assert response.status == 200
    products = _products_from_response(response.json())
    assert products, "The sorted products response contained no products."
    first_name = products[0].get("name")
    assert isinstance(first_name, str) and first_name, products[0]

    # The response is received just before Angular replaces the old product
    # cards.  Waiting for the first response product prevents sampling a
    # stale DOM while retaining the ascending-price assertion below.
    expect(home.product_headings.first).to_have_text(first_name)

    prices = home.get_product_prices()
    assert prices, "No product prices were rendered after sorting."
    assert prices == sorted(prices), (
        f"Sort value={home.sort_select.input_value()}; prices are not ascending: {prices}"
    )


@pytest.mark.regression
def test_price_slider_limits_rendered_products_to_selected_maximum(
    page: Page, settings: ToolshopSettings
) -> None:
    """Objective: use price range. Precondition: both sliders exist. Expected: maximum slider and visible prices obey 50."""

    home = HomePage(page, settings)
    home.open()
    home.set_price_range(minimum=0, maximum=50)

    expect(home.price_sliders.nth(1)).to_have_attribute("aria-valuenow", "50")
    expect(home.product_links.first).to_be_visible()
    assert all(price <= Decimal("50") for price in home.get_product_prices())
