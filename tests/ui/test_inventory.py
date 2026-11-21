import pytest
from playwright.sync_api import expect

from pages import InventoryPage


@pytest.mark.smoke
def test_catalog_lists_six_products(inventory: InventoryPage):
    expect(inventory.items).to_have_count(6)


@pytest.mark.parametrize(
    "option, key, reverse",
    [
        (InventoryPage.SORT_A_TO_Z, "names", False),
        (InventoryPage.SORT_Z_TO_A, "names", True),
        (InventoryPage.SORT_PRICE_LOW_HIGH, "prices", False),
        (InventoryPage.SORT_PRICE_HIGH_LOW, "prices", True),
    ],
    ids=["name-a-z", "name-z-a", "price-low-high", "price-high-low"],
)
def test_sorting(inventory: InventoryPage, option, key, reverse):
    inventory.sort_by(option)

    values = getattr(inventory, key)()
    assert values == sorted(values, reverse=reverse), f"{option} sort gave {values}"


def test_cart_badge_tracks_add_and_remove(inventory: InventoryPage):
    expect(inventory.cart_badge).to_have_count(0)

    inventory.add_to_cart("Sauce Labs Backpack")
    inventory.add_to_cart("Sauce Labs Bike Light")
    expect(inventory.cart_badge).to_have_text("2")

    inventory.remove_from_cart("Sauce Labs Backpack")
    expect(inventory.cart_badge).to_have_text("1")

    inventory.remove_from_cart("Sauce Labs Bike Light")
    expect(inventory.cart_badge).to_have_count(0)
