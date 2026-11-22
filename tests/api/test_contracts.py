"""Contract tests: every response must keep the shape clients depend on."""

import pytest

import config
from api import BookingClient
from api.schemas import (
    BOOKING,
    BOOKING_ID_LIST,
    CREATE_BOOKING_RESPONSE,
    TOKEN_RESPONSE,
    assert_matches,
)


def test_auth_response_contract(api_request):
    response = BookingClient(api_request).create_token(config.API_USERNAME, config.API_PASSWORD)

    assert_matches(response.json(), TOKEN_RESPONSE)


@pytest.mark.smoke
def test_create_booking_contract(client: BookingClient, booking_payload):
    response = client.create_booking(booking_payload)
    body = response.json()

    assert_matches(body, CREATE_BOOKING_RESPONSE)
    client.delete_booking(body["bookingid"])


def test_get_booking_contract(client: BookingClient, booking):
    assert_matches(client.get_booking(booking).json(), BOOKING)


def test_list_bookings_contract(client: BookingClient, booking):
    assert_matches(client.list_bookings().json(), BOOKING_ID_LIST)


def test_schema_rejects_wrong_types():
    """Guard the guard: the schema itself must catch a broken response."""
    broken = {
        "firstname": "Deep",
        "lastname": "Patel",
        "totalprice": "420",  # string instead of integer
        "depositpaid": True,
        "bookingdates": {"checkin": "2027-01-10", "checkout": "2027-01-14"},
    }

    with pytest.raises(AssertionError, match="is not of type 'integer'"):
        assert_matches(broken, BOOKING)
