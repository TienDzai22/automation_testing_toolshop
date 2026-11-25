"""Data-driven UI checks for Toolshop product search."""

import json
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from src.config.settings import ToolshopSettings
from src.pages.home_page import HomePage


SEARCH_CASES = json.loads(
    (Path(__file__).parents[2] / "data" / "search_cases.json").read_text(encoding="utf-8")
)


def _response_product_names(payload: object) -> list[str]:
    """Read product names from Toolshop's paginated search response."""

    if isinstance(payload, dict):
        products = payload.get("data", payload.get("products", []))
    else:
        products = payload
    if not isinstance(products, list):
        raise AssertionError(f"Unexpected search response shape: {payload!r}")
    return [
        product["name"].strip()
        for product in products
        if isinstance(product, dict) and isinstance(product.get("name"), str)
    ]


@pytest.mark.regression
@pytest.mark.parametrize(
    ("query", "expected_name_fragment"),
    [
        (case["query"], case["expected_name_fragment"])
        for case in SEARCH_CASES
    ],
    ids=[case["query"] for case in SEARCH_CASES],
)
def test_search_returns_only_products_matching_json_case(
    page: Page,
    settings: ToolshopSettings,
    query: str,
    expected_name_fragment: str,
) -> None:
    """Each JSON case must yield real product names matching its expected fragment."""

    home = HomePage(page, settings)
    home.open()
    expect(home.product_headings.first).to_be_visible(timeout=15_000)
    with page.expect_response(
        lambda response: response.url.startswith(f"{settings.api_url}/products")
        and (
            query.casefold() in response.url.casefold()
            or query.casefold() in (response.request.post_data or "").casefold()
        )
    ) as response_info:
        home.search(query)
    assert response_info.value.status == 200

    names = _response_product_names(response_info.value.json())
    assert names, f"Search for {query!r} returned no product names."
    assert all(expected_name_fragment.casefold() in name.casefold() for name in names), (
        f"Search API returned non-matching products for {query!r}: {names}."
    )


@pytest.mark.regression
def test_search_unknown_keyword_returns_no_product_cards(page: Page, settings: ToolshopSettings) -> None:
    """Objective: search a missing term. Precondition: home is open. Expected: no product card is rendered."""

    home = HomePage(page, settings)
    home.open()
    home.search("no-product-should-match-this-qa-search")

    expect(home.product_links).to_have_count(0)
