from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """Covers all three checkout steps: your info, overview, complete."""

    path = "/checkout-step-one.html"

    def __init__(self, page):
        super().__init__(page)
        # Step one: customer info
        self.first_name = page.locator('[data-test="firstName"]')
        self.last_name = page.locator('[data-test="lastName"]')
        self.postal_code = page.locator('[data-test="postalCode"]')
        self.continue_button = page.locator('[data-test="continue"]')
        self.error = page.locator('[data-test="error"]')
        # Step two: overview
        self.subtotal = page.locator(".summary_subtotal_label")
        self.tax = page.locator(".summary_tax_label")
        self.total = page.locator(".summary_total_label")
        self.finish_button = page.locator('[data-test="finish"]')
        # Step three: complete
        self.complete_header = page.locator(".complete-header")

    def fill_info(self, first: str, last: str, postal: str):
        self.first_name.fill(first)
        self.last_name.fill(last)
        self.postal_code.fill(postal)
        self.continue_button.click()

    def amounts(self) -> tuple[float, float, float]:
        return (
            self.parse_price(self.subtotal.inner_text()),
            self.parse_price(self.tax.inner_text()),
            self.parse_price(self.total.inner_text()),
        )

    def finish(self):
        self.finish_button.click()
