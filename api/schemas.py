"""JSON Schemas for Restful Booker responses.

Equality checks catch wrong values; schemas catch contract drift, such as a
field changing type, going missing, or extra fields appearing."""

from jsonschema import validate

DATE = {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"}

BOOKING = {
    "type": "object",
    "required": ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
    "properties": {
        "firstname": {"type": "string"},
        "lastname": {"type": "string"},
        "totalprice": {"type": "integer", "minimum": 0},
        "depositpaid": {"type": "boolean"},
        "bookingdates": {
            "type": "object",
            "required": ["checkin", "checkout"],
            "properties": {"checkin": DATE, "checkout": DATE},
            "additionalProperties": False,
        },
        "additionalneeds": {"type": "string"},
    },
    "additionalProperties": False,
}

CREATE_BOOKING_RESPONSE = {
    "type": "object",
    "required": ["bookingid", "booking"],
    "properties": {"bookingid": {"type": "integer"}, "booking": BOOKING},
    "additionalProperties": False,
}

BOOKING_ID_LIST = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["bookingid"],
        "properties": {"bookingid": {"type": "integer"}},
    },
}

TOKEN_RESPONSE = {
    "type": "object",
    "required": ["token"],
    "properties": {"token": {"type": "string", "minLength": 1}},
    "additionalProperties": False,
}


def assert_matches(instance, schema):
    """Raise a readable AssertionError instead of a jsonschema traceback."""
    try:
        validate(instance=instance, schema=schema)
    except Exception as exc:  # jsonschema.ValidationError
        raise AssertionError(f"Response does not match schema: {exc.message}") from None
