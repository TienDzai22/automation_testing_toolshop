"""Page object for the Toolshop contact form."""

from __future__ import annotations

from src.pages.base_page import BasePage


class ContactPage(BasePage):
    """Expose contact-form inputs and attachment upload without assertions."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.first_name_input = self.by_test_id("first-name")
        self.last_name_input = self.by_test_id("last-name")
        self.email_input = self.by_test_id("email")
        self.subject_select = self.by_test_id("subject")
        self.message_input = self.by_test_id("message")
        self.attachment_input = self.by_test_id("attachment")
        self.submit_button = self.by_test_id("contact-submit")
        self.result_message = self.page.locator("[role='alert'], .alert")

    def open(self) -> None:
        """Open the contact route."""

        self.open_path("/contact")

    def fill_contact_form(
        self,
        first_name: str,
        last_name: str,
        email: str,
        subject: str,
        message: str,
    ) -> None:
        """Fill all required contact fields using displayed subject text."""

        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.email_input.fill(email)
        self.subject_select.select_option(label=subject)
        self.message_input.fill(message)

    def upload_empty_file(
        self, file_name: str = "empty-attachment.txt", mime_type: str = "text/plain"
    ) -> None:
        """Attach an in-memory, zero-byte file without creating a local artifact."""

        self.attachment_input.set_input_files(
            {"name": file_name, "mimeType": mime_type, "buffer": b""}
        )

    def submit(self) -> None:
        """Submit the completed contact form."""

        self.submit_button.click()

    def get_result_message(self) -> str:
        """Return the currently rendered contact outcome text."""

        return self.result_message.first.inner_text()
