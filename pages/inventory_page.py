from pages.base_page import BasePage


def slug(product_name: str) -> str:
    """'Sauce Labs Backpack' -> 'sauce-labs-backpack' (matches the site's data-test ids)."""
    return product_name.lower().replace(" ", "-")


class InventoryPage(BasePage):
    path = "/inventory.html"

    SORT_A_TO_Z = "az"
    SORT_Z_TO_A = "za"
    SORT_PRICE_LOW_HIGH = "lohi"
    SORT_PRICE_HIGH_LOW = "hilo"

    def __init__(self, page):
        super().__init__(page)
        self.title = page.locator(".title")
        self.items = page.locator(".inventory_item")
        self.item_names = page.locator(".inventory_item_name")
        self.item_prices = page.locator(".inventory_item_price")
        self.sort_select = page.locator('[data-test="product-sort-container"]')
        self.cart_badge = page.locator(".shopping_cart_badge")
        self.cart_link = page.locator(".shopping_cart_link")

    def add_to_cart(self, product_name: str):
        self.page.locator(f'[data-test="add-to-cart-{slug(product_name)}"]').click()

    def remove_from_cart(self, product_name: str):
        self.page.locator(f'[data-test="remove-{slug(product_name)}"]').click()

    def sort_by(self, option: str):
        self.sort_select.select_option(option)

    def names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def prices(self) -> list[float]:
        return [self.parse_price(t) for t in self.item_prices.all_inner_texts()]

    def go_to_cart(self):
        self.cart_link.click()
