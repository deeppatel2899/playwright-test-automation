"""Thin client for the Restful Booker API, built on Playwright's APIRequestContext.

Tests talk to this class instead of raw URLs, so an endpoint change is a
one-line fix here rather than a hunt through every test."""

from playwright.sync_api import APIRequestContext, APIResponse


class BookingClient:
    def __init__(self, request: APIRequestContext):
        self.request = request
        self._token: str | None = None

    # --- auth -------------------------------------------------------------
    def create_token(self, username: str, password: str) -> APIResponse:
        return self.request.post("/auth", data={"username": username, "password": password})

    def login(self, username: str, password: str) -> str:
        response = self.create_token(username, password)
        token = response.json().get("token")
        if not token:
            raise RuntimeError(f"Auth failed: {response.text()}")
        self._token = token
        return token

    def _auth_headers(self) -> dict:
        if not self._token:
            raise RuntimeError("Call login() before using endpoints that need auth")
        return {"Cookie": f"token={self._token}"}

    # --- bookings ---------------------------------------------------------
    def ping(self) -> APIResponse:
        return self.request.get("/ping")

    def list_bookings(self, **filters) -> APIResponse:
        return self.request.get("/booking", params=filters or None)

    def get_booking(self, booking_id: int) -> APIResponse:
        return self.request.get(f"/booking/{booking_id}")

    def create_booking(self, booking: dict) -> APIResponse:
        return self.request.post("/booking", data=booking)

    def update_booking(self, booking_id: int, booking: dict) -> APIResponse:
        return self.request.put(f"/booking/{booking_id}", data=booking, headers=self._auth_headers())

    def partial_update_booking(self, booking_id: int, fields: dict) -> APIResponse:
        return self.request.patch(f"/booking/{booking_id}", data=fields, headers=self._auth_headers())

    def delete_booking(self, booking_id: int, authenticated: bool = True) -> APIResponse:
        headers = self._auth_headers() if authenticated else {}
        return self.request.delete(f"/booking/{booking_id}", headers=headers)
