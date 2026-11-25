"""Page object for Toolshop cart and checkout controls."""

from __future__ import annotations

import re

from playwright.sync_api import Locator

from src.pages.base_page import BasePage


class CartPage(BasePage):
    """Expose cart controls when the selected Toolshop environment renders them."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cart_link = self.page.get_by_role("link", name=re.compile(r"cart", re.IGNORECASE))
        self.cart_rows = self.page.get_by_role("row")
        self.product_titles = self.by_test_id("product-title")
        self.quantity_inputs = self.by_test_id("product-quantity")
        self.remove_buttons = self.page.locator("table tbody tr td:last-child .btn-danger")
        self.checkout_button = self.page.get_by_role(
            "button", name=re.compile(r"checkout", re.IGNORECASE)
        )
        self.total_text = self.by_test_id("cart-total")

    def open(self) -> None:
        """Open the cart through its header link when a browser cart session exists."""

        if self.cart_link.count():
            self.cart_link.click()
            return
        self.open_path("/checkout")

    def get_items(self) -> Locator:
        """Return the rendered cart rows for test-level inspection."""

        return self.cart_rows

    def set_quantity(self, item_index: int, quantity: int) -> None:
        """Change the quantity for one cart line by its current visual index."""

        if quantity < 1:
            raise ValueError("Cart item quantity must be at least one.")
        quantity_input = self.quantity_inputs.nth(item_index)
        quantity_input.fill(str(quantity))
        quantity_input.press("Tab")

    def remove_item(self, item_index: int) -> None:
        """Remove one cart line by its current visual index."""

        self.remove_buttons.nth(item_index).click()

    def get_total(self) -> str:
        """Return the rendered cart total text."""

        return self.total_text.first.inner_text()

    def proceed_to_checkout(self) -> None:
        """Continue from a rendered cart to checkout."""

        self.checkout_button.click()
