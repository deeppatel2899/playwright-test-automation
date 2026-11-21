import re

import pytest
from playwright.sync_api import expect

from pages import CartPage, CheckoutPage, InventoryPage

PRODUCTS = ["Sauce Labs Backpack", "Sauce Labs Bolt T-Shirt"]


@pytest.fixture
def checkout(inventory: InventoryPage) -> CheckoutPage:
    """Cart with two products, on step one of checkout."""
    for product in PRODUCTS:
        inventory.add_to_cart(product)
    inventory.go_to_cart()
    CartPage(inventory.page).checkout()
    return CheckoutPage(inventory.page)


def test_cart_shows_added_products(inventory: InventoryPage):
    for product in PRODUCTS:
        inventory.add_to_cart(product)
    inventory.go_to_cart()

    cart = CartPage(inventory.page)
    expect(cart.items).to_have_count(len(PRODUCTS))
    assert sorted(cart.names()) == sorted(PRODUCTS)


@pytest.mark.smoke
def test_end_to_end_purchase(checkout: CheckoutPage):
    checkout.fill_info("Deep", "Patel", "V2N 4Z9")
    expect(checkout.page).to_have_url(re.compile(r"/checkout-step-two\.html$"))

    subtotal, tax, total = checkout.amounts()
    assert subtotal == pytest.approx(29.99 + 15.99)
    assert total == pytest.approx(subtotal + tax), "total should equal subtotal + tax"

    checkout.finish()
    expect(checkout.complete_header).to_have_text("Thank you for your order!")


@pytest.mark.parametrize(
    "first, last, postal, message",
    [
        ("", "Patel", "V2N 4Z9", "First Name is required"),
        ("Deep", "", "V2N 4Z9", "Last Name is required"),
        ("Deep", "Patel", "", "Postal Code is required"),
    ],
    ids=["missing-first", "missing-last", "missing-postal"],
)
def test_checkout_requires_customer_info(checkout: CheckoutPage, first, last, postal, message):
    checkout.fill_info(first, last, postal)

    expect(checkout.error).to_contain_text(message)
    expect(checkout.page).to_have_url(re.compile(r"/checkout-step-one\.html$"))
