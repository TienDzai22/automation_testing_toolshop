"""UI checks for Toolshop contact form behaviour."""

import secrets
import re

import pytest
from playwright.sync_api import Page, expect

from src.config.settings import ToolshopSettings
from src.pages.contact_page import ContactPage


@pytest.mark.regression
def test_contact_empty_required_fields_show_validation(page: Page, settings: ToolshopSettings) -> None:
    """Objective: validate Contact. Precondition: form is empty. Expected: required subject and message are invalid."""

    contact = ContactPage(page, settings)
    contact.open()
    contact.submit()

    expect(contact.subject_select).to_have_attribute("class", re.compile(r"ng-invalid"))
    expect(contact.message_input).to_have_attribute("class", re.compile(r"ng-invalid"))


@pytest.mark.regression
def test_contact_zero_byte_file_can_be_attached_to_completed_form(
    page: Page, settings: ToolshopSettings
) -> None:
    """Objective: attach zero-byte file. Precondition: required contact fields are valid. Expected: attachment input holds it."""

    contact = ContactPage(page, settings)
    contact.open()
    contact.fill_contact_form(
        first_name="UI",
        last_name="Automation",
        email=f"contact.{secrets.token_hex(8)}@example.test",
        subject="Customer service",
        message=(
            "Automated contact submission validates a zero-byte attachment and "
            "the meaningful success outcome returned by Toolshop."
        ),
    )
    contact.upload_empty_file()

    expect(contact.attachment_input).to_have_value(re.compile(r"empty-attachment\.txt$"))
    contact.submit()
    expect(contact.result_message.first).to_be_visible()
    expect(contact.result_message.first).to_contain_text(
        re.compile(r"success|thank|received|sent", re.IGNORECASE)
    )


@pytest.mark.regression
def test_footer_github_link_opens_project_in_new_tab(page: Page, settings: ToolshopSettings) -> None:
    """Objective: open GitHub footer. Precondition: home is open. Expected: a new tab reaches the Toolshop repository."""

    contact = ContactPage(page, settings)
    contact.open()
    with page.context.expect_page() as new_page_info:
        contact.github_footer_link.click()
    github_page = new_page_info.value
    github_page.wait_for_load_state("domcontentloaded")

    expect(github_page).to_have_url(
        re.compile(r"github\.com/testsmith-io/practice-software-testing/?$")
    )
