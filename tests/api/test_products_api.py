"""Product API contract checks using only public, documented endpoints."""

from numbers import Real

import pytest
from playwright.sync_api import APIRequestContext


def _products_from_payload(payload: object) -> list[dict[str, object]]:
    """Return a typed page of products from Toolshop's documented envelope."""

    assert isinstance(payload, dict), f"Expected a JSON object, got {type(payload).__name__}."
    assert isinstance(payload.get("current_page"), int), payload
    assert isinstance(payload.get("total"), int), payload
    products = payload.get("data")
    assert isinstance(products, list), payload
    return [product for product in products if isinstance(product, dict)]


@pytest.mark.api
def test_product_list_has_documented_pagination_and_product_types(
    api_context: APIRequestContext,
) -> None:
    """TC_API_02: GET /products returns a valid paginated product representation."""

    response = api_context.get("/products")

    assert response.status == 200, response.text()
    products = _products_from_payload(response.json())
    assert products, "The product list contained no products."
    product = products[0]
    assert isinstance(product.get("id"), str) and product["id"], product
    assert isinstance(product.get("name"), str) and product["name"], product
    assert isinstance(product.get("description"), str), product
    assert isinstance(product.get("price"), Real) and not isinstance(product["price"], bool), product
    assert isinstance(product.get("in_stock"), bool), product
    assert isinstance(product.get("is_rental"), bool), product


@pytest.mark.api
def test_product_search_returns_only_names_matching_query(
    api_context: APIRequestContext,
) -> None:
    """TC_API_03: documented name search returns products matching the supplied query."""

    query = "hammer"
    response = api_context.get("/products/search", params={"q": query})

    assert response.status == 200, response.text()
    products = _products_from_payload(response.json())
    assert products, f"Search for {query!r} returned no products."
    names = [product.get("name") for product in products]
    assert all(isinstance(name, str) and query in name.casefold() for name in names), names


@pytest.mark.api
def test_unknown_product_id_returns_documented_not_found_status(
    api_context: APIRequestContext,
) -> None:
    """TC_API_04: an unknown product identifier receives the OpenAPI 404 response."""

    response = api_context.get("/products/not-a-real-product")

    assert response.status == 404, response.text()
