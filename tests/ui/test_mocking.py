"""Route-interception checks for Toolshop catalogue behaviour."""

from __future__ import annotations

from urllib.parse import urlsplit

import pytest
from playwright.sync_api import Page, Request, Route, expect

from src.config.settings import ToolshopSettings
from src.pages.home_page import HomePage


def _is_products_list_request(request: Request, settings: ToolshopSettings) -> bool:
    """Match only the catalogue endpoint used by the configured environment."""

    request_url = urlsplit(request.url)
    api_url = urlsplit(settings.api_url)
    return (
        request_url.scheme == api_url.scheme
        and request_url.netloc == api_url.netloc
        and request_url.path.rstrip("/") == f"{api_url.path.rstrip('/')}/products"
        and request.method in {"GET", "QUERY"}
    )


@pytest.mark.regression
def test_blocking_product_images_keeps_catalogue_content_available(
    page: Page, settings: ToolshopSettings
) -> None:
    """TC_MOCK_01: aborted image requests must not stop names and prices rendering."""

    blocked_image_urls: list[str] = []

    def abort_image(route: Route) -> None:
        if route.request.resource_type == "image":
            blocked_image_urls.append(route.request.url)
            route.abort()
            return
        route.continue_()

    page.route("**/*", abort_image)
    try:
        home = HomePage(page, settings)
        home.open()

        expect(home.product_headings.first).to_be_visible()
        expect(home.product_links.first).to_be_visible()
        assert home.get_first_product_name().strip(), "No product name was rendered."
        assert home.get_product_prices(), "No product price was rendered."
        assert blocked_image_urls, "The catalogue did not issue an image request to abort."
    finally:
        page.unroute("**/*", abort_image)


@pytest.mark.regression
def test_mocking_empty_products_response_renders_an_empty_catalogue(
    page: Page, settings: ToolshopSettings
) -> None:
    """TC_MOCK_02: a live products contract can be fulfilled with an empty page."""

    intercepted_urls: list[str] = []

    def fulfill_empty_products(route: Route) -> None:
        if not _is_products_list_request(route.request, settings):
            route.continue_()
            return

        # Fetching first preserves the real endpoint's current envelope instead
        # of inventing a response shape.  Only the product collection and its
        # pagination totals are changed for this browser request.
        upstream_response = route.fetch()
        assert upstream_response.status == 200
        payload = upstream_response.json()
        assert isinstance(payload, dict), payload
        assert isinstance(payload.get("data"), list), payload

        empty_payload = dict(payload)
        empty_payload["data"] = []
        empty_payload["total"] = 0
        for field in ("from", "to"):
            if field in empty_payload:
                empty_payload[field] = None
        if "last_page" in empty_payload:
            empty_payload["last_page"] = 1

        intercepted_urls.append(route.request.url)
        route.fulfill(response=upstream_response, json=empty_payload)

    page.route("**/*", fulfill_empty_products)
    try:
        home = HomePage(page, settings)
        with page.expect_response(
            lambda response: _is_products_list_request(response.request, settings)
        ) as response_info:
            home.open()

        assert response_info.value.status == 200
        assert intercepted_urls, "The products API request was not intercepted."
        expect(home.product_links).to_have_count(0)
        expect(home.product_headings).to_have_count(0)
        expect(home.search_input).to_be_visible()
    finally:
        page.unroute("**/*", fulfill_empty_products)
