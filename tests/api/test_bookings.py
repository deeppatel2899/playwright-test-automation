import pytest

from api import BookingClient


@pytest.mark.smoke
def test_create_booking_echoes_payload(client: BookingClient, booking_payload):
    response = client.create_booking(booking_payload)

    assert response.status == 200
    body = response.json()
    assert isinstance(body["bookingid"], int)
    assert body["booking"] == booking_payload

    client.delete_booking(body["bookingid"])


def test_get_booking_by_id(client: BookingClient, booking, booking_payload):
    response = client.get_booking(booking)

    assert response.status == 200
    assert response.json() == booking_payload


def test_filter_bookings_by_name(client: BookingClient, booking, booking_payload):
    response = client.list_bookings(
        firstname=booking_payload["firstname"], lastname=booking_payload["lastname"]
    )

    assert response.status == 200
    ids = [b["bookingid"] for b in response.json()]
    assert booking in ids


def test_full_update(client: BookingClient, booking, booking_payload):
    updated = {**booking_payload, "totalprice": 500, "additionalneeds": "Late checkout"}

    response = client.update_booking(booking, updated)

    assert response.status == 200
    assert response.json() == updated
    assert client.get_booking(booking).json() == updated


def test_partial_update_changes_only_given_fields(client: BookingClient, booking, booking_payload):
    response = client.partial_update_booking(booking, {"firstname": "Deepkumar"})

    assert response.status == 200
    assert response.json() == {**booking_payload, "firstname": "Deepkumar"}


def test_delete_booking(client: BookingClient, booking_payload):
    booking_id = client.create_booking(booking_payload).json()["bookingid"]

    assert client.delete_booking(booking_id).status == 201
    assert client.get_booking(booking_id).status == 404


def test_delete_without_token_is_forbidden(client: BookingClient, booking):
    response = client.delete_booking(booking, authenticated=False)

    assert response.status == 403
    assert client.get_booking(booking).status == 200, "booking should still exist"


def test_unknown_booking_returns_404(client: BookingClient):
    assert client.get_booking(999_999_999).status == 404


@pytest.mark.xfail(
    reason="Known defect: API returns 500 instead of 400 for a missing required field",
    strict=True,
)
def test_missing_required_field_returns_400(client: BookingClient, booking_payload):
    incomplete = {k: v for k, v in booking_payload.items() if k != "firstname"}

    assert client.create_booking(incomplete).status == 400
