from playwright.sync_api import Page

import config


class BasePage:
    """Shared plumbing for every page object."""

    path = "/"

    def __init__(self, page: Page):
        self.page = page

    def open(self):
        self.page.goto(config.UI_BASE_URL + self.path)
        return self

    @staticmethod
    def parse_price(text: str) -> float:
        """'$29.99' or 'Total: $32.39' -> 29.99 / 32.39"""
        return float(text.split("$")[-1])
