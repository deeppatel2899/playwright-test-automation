import pytest

import config
from api import BookingClient


@pytest.mark.smoke
def test_health_check(api_request):
    assert BookingClient(api_request).ping().status == 201


def test_valid_credentials_return_token(api_request):
    response = BookingClient(api_request).create_token(config.API_USERNAME, config.API_PASSWORD)

    assert response.status == 200
    token = response.json().get("token")
    assert isinstance(token, str) and token


def test_bad_credentials_are_rejected(api_request):
    response = BookingClient(api_request).create_token(config.API_USERNAME, "not-the-password")

    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"
