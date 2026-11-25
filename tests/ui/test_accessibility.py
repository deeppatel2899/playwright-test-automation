"""Accessibility regression checks for the main shopping journey.

Each page is scanned with axe-core and compared with `a11y/baseline.json`.
See `a11y/__init__.py` for why a baseline is used instead of zero tolerance.
"""

import warnings

import pytest
from playwright.sync_api import expect

import a11y
from pages import CartPage, CheckoutPage

BASELINE = a11y.load_baseline()


# Each opener takes pytest's `request` and pulls in only the fixtures it needs,
# so the login page is scanned logged out and the rest as a logged-in user.
def _open_login(request):
    return request.getfixturevalue("login_page").page


def _open_inventory(request):
    return request.getfixturevalue("inventory").page


def _open_cart(request):
    inventory = request.getfixturevalue("inventory")
    inventory.add_to_cart("Sauce Labs Backpack")
    inventory.go_to_cart()
    expect(CartPage(inventory.page).items).to_have_count(1)
    return inventory.page


def _open_checkout(request):
    page = _open_cart(request)
    CartPage(page).checkout()
    expect(CheckoutPage(page).first_name).to_be_visible()
    return page


PAGES = {
    "login": _open_login,
    "inventory": _open_inventory,
    "cart": _open_cart,
    "checkout": _open_checkout,
}


@pytest.mark.parametrize("name", PAGES)
def test_no_new_serious_accessibility_violations(name, request):
    found = a11y.scan(PAGES[name](request))
    known = BASELINE[name]

    fixed = a11y.fixed_rules(found, known)
    if fixed:
        warnings.warn(
            f"{name}: baseline rules no longer fail, remove them from a11y/baseline.json: {fixed}",
            stacklevel=2,
        )

    new = a11y.new_violations(found, known)
    blocking = [v for v in new if v.impact in a11y.BLOCKING_IMPACTS]
    report = "\n".join(str(v) for v in new)
    assert not blocking, f"{name} has new serious/critical accessibility violations:\n{report}"


def test_baseline_covers_every_scanned_page():
    assert set(BASELINE) == set(PAGES)


def test_gate_logic_flags_only_rules_missing_from_baseline():
    found = [
        a11y.Violation("region", "moderate", "Content in landmarks", ("div",)),
        a11y.Violation("color-contrast", "serious", "Enough contrast", ("button",)),
    ]

    assert [v.rule for v in a11y.new_violations(found, ["region"])] == ["color-contrast"]
    assert a11y.fixed_rules(found, ["region", "label"]) == ["label"]
