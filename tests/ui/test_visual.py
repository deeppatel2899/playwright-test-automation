"""Visual regression checks for the main shopping journey.

Each screen is compared with a baseline PNG in `visual/baselines/<browser>/`.
See `visual/__init__.py` for the tolerance rules and how to update baselines.
"""

import allure
import pytest
from PIL import Image, ImageDraw
from playwright.sync_api import Page, expect

import config
import visual
from pages import CartPage, InventoryPage

pytestmark = pytest.mark.visual


def _open_login(request) -> Page:
    return request.getfixturevalue("login_page").page


def _open_inventory(request) -> Page:
    return request.getfixturevalue("inventory").page


def _open_product(request) -> Page:
    inventory = request.getfixturevalue("inventory")
    inventory.item_names.filter(has_text="Sauce Labs Backpack").click()
    expect(inventory.page.locator(".inventory_details_name")).to_have_text("Sauce Labs Backpack")
    return inventory.page


def _open_cart(request) -> Page:
    inventory = request.getfixturevalue("inventory")
    inventory.add_to_cart("Sauce Labs Backpack")
    inventory.go_to_cart()
    expect(CartPage(inventory.page).items).to_have_count(1)
    return inventory.page


SCREENS = {
    "login": _open_login,
    "inventory": _open_inventory,
    "product": _open_product,
    "cart": _open_cart,
}


def screenshot(page: Page) -> Image.Image:
    page.set_viewport_size(visual.VIEWPORT)
    page.wait_for_load_state("networkidle")
    return visual.load(page.screenshot(animations="disabled", caret="hide"))


@pytest.mark.parametrize("name", SCREENS)
def test_screen_matches_baseline(name, request, browser_name):
    actual = screenshot(SCREENS[name](request))
    baseline = visual.baseline_path(browser_name, name)

    if request.config.getoption("--update-snapshots"):
        baseline.parent.mkdir(parents=True, exist_ok=True)
        actual.save(baseline)
        pytest.skip(f"baseline written to {baseline}")

    assert baseline.exists(), f"no baseline for {browser_name}/{name}, record one with --update-snapshots"
    result = visual.compare(actual, visual.load(baseline))

    if not result.passed:
        out = visual.save_failure_artifacts(browser_name, name, actual, result)
        if result.diff_image is not None:
            allure.attach.file(
                out / f"{name}-diff.png", name="visual diff", attachment_type=allure.attachment_type.PNG
            )
    assert result.size_matches, f"visual regression on {name}: size {actual.size} differs from baseline"
    assert result.passed, (
        f"visual regression on {name}: {result.diff_ratio:.2%} of pixels changed "
        f"(limit {visual.MAX_DIFF_RATIO:.0%}), see {visual.OUTPUT_DIR}"
    )


def test_problem_user_broken_images_are_caught(login_page, browser_name):
    """problem_user sees the wrong product photos while every DOM check still
    passes. The visual check must flag that, or its tolerance is too loose."""
    baseline = visual.baseline_path(browser_name, "inventory")
    if not baseline.exists():
        pytest.skip("inventory baseline not recorded yet")

    login_page.login(config.PROBLEM_USER, config.UI_PASSWORD)
    expect(InventoryPage(login_page.page).items).to_have_count(6)
    result = visual.compare(screenshot(login_page.page), visual.load(baseline))

    assert not result.passed, f"only {result.diff_ratio:.2%} changed, broken images went unnoticed"


def _blank(size=(100, 100)) -> Image.Image:
    return Image.new("RGB", size, "white")


def test_comparator_ignores_noise_but_flags_real_changes():
    noisy = _blank()
    noisy.putpixel((5, 5), (230, 230, 230))  # anti-aliasing sized change
    assert visual.compare(noisy, _blank()).passed

    changed = _blank()
    ImageDraw.Draw(changed).rectangle((0, 0, 19, 19), fill="black")  # 4% of the image
    result = visual.compare(changed, _blank())
    assert not result.passed
    assert result.diff_ratio == pytest.approx(0.04)

    assert not visual.compare(_blank((100, 101)), _blank()).size_matches
