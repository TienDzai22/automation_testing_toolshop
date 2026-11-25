"""Public API availability checks documented by the Toolshop OpenAPI contract."""

import pytest
from playwright.sync_api import APIRequestContext


@pytest.mark.api
def test_brands_endpoint_is_available_and_returns_brand_objects(
    api_context: APIRequestContext,
) -> None:
    """TC_API_01: the documented public brands endpoint returns typed JSON data."""

    response = api_context.get("/brands")

    assert response.status == 200, response.text()
    payload = response.json()
    assert isinstance(payload, list), f"Expected an array of brands, got {type(payload).__name__}."
    assert payload, "The public brands endpoint returned no brands."
    first_brand = payload[0]
    assert isinstance(first_brand, dict)
    assert isinstance(first_brand.get("id"), str) and first_brand["id"], first_brand
    assert isinstance(first_brand.get("name"), str) and first_brand["name"], first_brand
