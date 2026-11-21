import re

import pytest
from playwright.sync_api import expect

import config
from pages import InventoryPage


@pytest.mark.smoke
def test_standard_user_can_log_in(login_page):
    login_page.login(config.STANDARD_USER, config.UI_PASSWORD)

    expect(login_page.page).to_have_url(re.compile(r"/inventory\.html$"))
    expect(InventoryPage(login_page.page).title).to_have_text("Products")


def test_locked_out_user_sees_error(login_page):
    login_page.login(config.LOCKED_OUT_USER, config.UI_PASSWORD)

    expect(login_page.error).to_contain_text("this user has been locked out")
    expect(login_page.page).not_to_have_url(re.compile(r"/inventory\.html$"))


@pytest.mark.parametrize(
    "username, password, message",
    [
        ("", "", "Username is required"),
        (config.STANDARD_USER, "", "Password is required"),
        (config.STANDARD_USER, "wrong_password", "do not match any user"),
        ("unknown_user", config.UI_PASSWORD, "do not match any user"),
    ],
    ids=["empty-both", "empty-password", "wrong-password", "unknown-user"],
)
def test_invalid_login_shows_validation_message(login_page, username, password, message):
    login_page.login(username, password)

    expect(login_page.error).to_be_visible()
    expect(login_page.error).to_contain_text(message)


def test_inventory_requires_login(page):
    """Deep-linking to a protected page while logged out should bounce to login."""
    InventoryPage(page).open()

    expect(page.locator('[data-test="error"]')).to_contain_text(
        "only access '/inventory.html' when you are logged in"
    )
