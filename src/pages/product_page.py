"""Page object for a Toolshop product detail page."""

from __future__ import annotations

import re

from src.pages.base_page import BasePage


class ProductPage(BasePage):
    """Expose product detail data and add-to-cart interactions."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.product_name = self.page.get_by_role("heading", level=1)
        self.price_text = self.page.get_by_text(re.compile(r"\$\d+(?:\.\d{2})?"))
        self.description_paragraphs = self.page.locator("p")
        self.quantity_input = self.page.get_by_role("spinbutton").first
        self.add_to_cart_button = self.page.get_by_role(
            "button", name=re.compile(r"add to cart", re.IGNORECASE)
        )

    def get_name(self) -> str:
        """Return the product name shown in the primary heading."""

        return self.product_name.inner_text()

    def get_price(self) -> str:
        """Return the first displayed currency value for this product."""

        return self.price_text.first.inner_text()

    def get_description(self) -> str:
        """Return the longest product paragraph, which is the detail description."""

        paragraphs = [text.strip() for text in self.description_paragraphs.all_inner_texts()]
        return max(paragraphs, key=len, default="")

    def set_quantity(self, quantity: int) -> None:
        """Set the product quantity using the page's accessible spinbutton."""

        if quantity < 1:
            raise ValueError("Product quantity must be at least one.")
        self.quantity_input.fill(str(quantity))

    def add_to_cart(self) -> None:
        """Add the currently selected quantity of this product to the cart."""

        self.add_to_cart_button.click()
