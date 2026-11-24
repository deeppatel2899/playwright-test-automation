"""Sauce Demo ships users with deliberate faults. These tests pin down that
behaviour: slow logins get a time budget, and known bugs are tracked with
xfail so the suite flags them the moment they change."""

import re
import time

import pytest
from playwright.sync_api import expect

import config
from pages import InventoryPage, LoginPage

LOGIN_BUDGET_SECONDS = 10


def test_performance_glitch_user_logs_in_within_budget(login_page):
    start = time.monotonic()
    login_page.login(config.PERFORMANCE_GLITCH_USER, config.UI_PASSWORD)
    expect(InventoryPage(login_page.page).title).to_have_text("Products", timeout=LOGIN_BUDGET_SECONDS * 1000)
    elapsed = time.monotonic() - start

    assert elapsed < LOGIN_BUDGET_SECONDS, f"login took {elapsed:.1f}s"


def test_performance_glitch_is_slower_than_standard(page):
    """The glitch should be measurable; if it vanishes, this test says so."""

    def timed_login(username: str) -> float:
        page.context.clear_cookies()
        login = LoginPage(page).open()
        start = time.monotonic()
        login.login(username, config.UI_PASSWORD)
        expect(page).to_have_url(re.compile(r"/inventory\.html$"), timeout=LOGIN_BUDGET_SECONDS * 1000)
        return time.monotonic() - start

    standard = timed_login(config.STANDARD_USER)
    glitchy = timed_login(config.PERFORMANCE_GLITCH_USER)

    assert glitchy > standard + 1, f"standard {standard:.1f}s vs glitch {glitchy:.1f}s"


@pytest.fixture
def problem_inventory(login_page) -> InventoryPage:
    login_page.login(config.PROBLEM_USER, config.UI_PASSWORD)
    inventory = InventoryPage(login_page.page)
    expect(inventory.title).to_have_text("Products")
    return inventory


def test_problem_user_still_sees_full_catalog(problem_inventory: InventoryPage):
    expect(problem_inventory.items).to_have_count(6)


@pytest.mark.xfail(reason="Known defect: problem_user sees the same image for every product", strict=True)
def test_problem_user_product_images_are_unique(problem_inventory: InventoryPage):
    images = problem_inventory.page.locator(".inventory_item img")
    sources = [images.nth(i).get_attribute("src") for i in range(images.count())]

    assert len(set(sources)) == len(sources), f"duplicate images: {sources}"


@pytest.mark.xfail(reason="Known defect: sorting has no effect for problem_user")
def test_problem_user_can_sort_by_price(problem_inventory: InventoryPage):
    problem_inventory.sort_by(InventoryPage.SORT_PRICE_LOW_HIGH)

    prices = problem_inventory.prices()
    assert prices == sorted(prices)
