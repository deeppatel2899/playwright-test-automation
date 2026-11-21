import pytest
from playwright.sync_api import Playwright

import config
from api import BookingClient


def pytest_collection_modifyitems(items):
    for item in items:
        if "tests/api" in str(item.fspath).replace("\\", "/"):
            item.add_marker(pytest.mark.api)


@pytest.fixture(scope="session")
def api_request(playwright: Playwright):
    context = playwright.request.new_context(
        base_url=config.API_BASE_URL,
        extra_http_headers={"Accept": "application/json"},
    )
    yield context
    context.dispose()


@pytest.fixture
def client(api_request) -> BookingClient:
    client = BookingClient(api_request)
    client.login(config.API_USERNAME, config.API_PASSWORD)
    return client


@pytest.fixture
def booking_payload() -> dict:
    return {
        "firstname": "Deep",
        "lastname": "Patel",
        "totalprice": 420,
        "depositpaid": True,
        "bookingdates": {"checkin": "2027-01-10", "checkout": "2027-01-14"},
        "additionalneeds": "Breakfast",
    }


@pytest.fixture
def booking(client: BookingClient, booking_payload: dict):
    """Create a booking for the test, and clean it up afterwards."""
    response = client.create_booking(booking_payload)
    assert response.ok, response.text()
    booking_id = response.json()["bookingid"]
    yield booking_id
    client.delete_booking(booking_id)
