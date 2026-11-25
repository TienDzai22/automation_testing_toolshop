"""Page object for Toolshop's product-listing home page."""

from __future__ import annotations

import re
from decimal import Decimal

from playwright.sync_api import Locator

from src.pages.base_page import BasePage


class HomePage(BasePage):
    """Expose home-page search, navigation, filters, and product links."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.category_menu = self.by_test_id("nav-categories")
        self.search_input = self.by_test_id("search-query")
        self.search_submit = self.by_test_id("search-submit")
        self.search_reset = self.by_test_id("search-reset")
        self.sort_select = self.by_test_id("sort")
        self.filters_toggle = self.by_test_id("filters").first
        self.price_sliders = self.page.get_by_role("slider")
        self.product_links = self.page.locator("a[href*='product/']")
        self.product_headings = self.page.get_by_role("heading", level=5)
        self.category_filters = self.page.locator("input[name='category_id']")
        self.leaf_category_filters = self.page.locator("ul input[name='category_id']")

    def open(self) -> None:
        """Open the configured Toolshop home route."""

        self.open_path()

    def search(self, query: str) -> None:
        """Submit a product search query."""

        self.search_input.fill(query)
        self.search_submit.click()

    def clear_search(self) -> None:
        """Clear the current search using Toolshop's reset control."""

        self.search_reset.click()

    def select_sort(self, option: str) -> None:
        """Select a visible sort option."""

        self.sort_select.select_option(label=option)

    def open_category(self, category_slug: str) -> None:
        """Open a category from the navigation menu using its stable slug."""

        self.category_menu.click()
        self.by_test_id(f"nav-{category_slug}").click()

    def filter_by_category(self, category_name: str, checked: bool = True) -> None:
        """Set a category checkbox by its accessible label."""

        self.page.get_by_role("checkbox", name=category_name, exact=True).set_checked(checked)

    def filter_by_brand(self, brand_name: str, checked: bool = True) -> None:
        """Set a brand checkbox by its accessible label."""

        self.page.get_by_role("checkbox", name=brand_name, exact=True).set_checked(checked)

    def set_price_range(self, minimum: int, maximum: int) -> None:
        """Set both price sliders using their keyboard-accessible controls."""

        self._set_slider_value(self.price_sliders.nth(0), minimum)
        self._set_slider_value(self.price_sliders.nth(1), maximum)

    def open_product(self, index: int = 0) -> None:
        """Open a visible product card without assuming its id or total count."""

        self.product_links.nth(index).click()

    def get_product_names(self) -> list[str]:
        """Return the currently rendered product-card names."""

        return [name.strip() for name in self.product_headings.all_inner_texts() if name.strip()]

    def get_first_product_name(self) -> str:
        """Return the first card's name, waiting on that card's own heading."""

        return self.product_links.first.get_by_role("heading", level=5).inner_text()

    def get_product_prices(self) -> list[Decimal]:
        """Extract one displayed price from each visible product card."""

        prices: list[Decimal] = []
        for card_text in self.product_links.all_inner_texts():
            matches = re.findall(r"\$(\d+(?:\.\d{2})?)", card_text)
            if matches:
                prices.append(Decimal(matches[-1]))
        return prices

    def select_first_category_filter(self) -> Locator:
        """Select the first available category without assuming a dynamic category id."""

        category_filter = self.category_filters.first
        category_filter.check()
        return category_filter

    @staticmethod
    def _set_slider_value(slider: Locator, value: int) -> None:
        """Move a range slider from its minimum using keyboard events."""

        if value < 0:
            raise ValueError("A price slider value cannot be negative.")
        slider.press("Home")
        for _ in range(value):
            slider.press("ArrowRight")
