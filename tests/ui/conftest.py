import pytest
from playwright.sync_api import Page, expect

import config
from pages import InventoryPage, LoginPage


def pytest_collection_modifyitems(items):
    for item in items:
        if "tests/ui" in str(item.fspath).replace("\\", "/"):
            item.add_marker(pytest.mark.ui)


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page).open()


@pytest.fixture
def inventory(login_page: LoginPage) -> InventoryPage:
    """A logged-in standard user, sitting on the products page."""
    login_page.login(config.STANDARD_USER, config.UI_PASSWORD)
    inventory = InventoryPage(login_page.page)
    expect(inventory.title).to_have_text("Products")
    return inventory
