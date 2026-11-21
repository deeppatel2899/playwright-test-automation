from pages.base_page import BasePage


class CartPage(BasePage):
    path = "/cart.html"

    def __init__(self, page):
        super().__init__(page)
        self.items = page.locator(".cart_item")
        self.item_names = page.locator(".inventory_item_name")
        self.checkout_button = page.locator('[data-test="checkout"]')

    def names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def checkout(self):
        self.checkout_button.click()
