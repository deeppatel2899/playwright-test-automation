import allure
import pytest
from playwright.sync_api import Page, expect

import config
from pages import InventoryPage, LoginPage


def pytest_collection_modifyitems(items):
    for item in items:
        if "tests/ui" in str(item.fspath).replace("\\", "/"):
            item.add_marker(pytest.mark.ui)


@pytest.fixture(autouse=True)
def _keep_request(request):
    # Lets the report hook below reach fixtures a test requested dynamically,
    # such as the accessibility tests' getfixturevalue("inventory").
    request.node.fixture_request = request


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """On a failed UI test, put the URL and a screenshot straight into the Allure
    report, so most failures can be triaged without downloading the trace.

    This runs right after the test body, while the page is still open."""
    report = yield
    request = getattr(item, "fixture_request", None)
    if report.when == "call" and report.failed and request and "page" in request.fixturenames:
        page: Page = request.getfixturevalue("page")
        if not page.is_closed():
            allure.attach(page.url, name="url", attachment_type=allure.attachment_type.URI_LIST)
            allure.attach(
                page.screenshot(full_page=True), name="screenshot", attachment_type=allure.attachment_type.PNG
            )
    return report


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
