from flask.testing import FlaskClient
from pydantic import BaseModel, Field, ValidationError
from pytest import raises
from werkzeug.exceptions import BadRequest

from app.handlers import reject_invalid_request


class Inner(BaseModel):
    size: int = Field(ge=1)


class Outer(BaseModel):
    inner: Inner
    name: str


def test_error_response(client: FlaskClient) -> None:
    resp = client.get("/invalid")
    assert resp.status_code == 404
    assert resp.is_json
    assert resp.get_json()["type"] == "not_found"


def test_invalid_request_lists_every_error_with_its_dotted_path() -> None:
    with raises(ValidationError) as validation:
        Outer.model_validate({"inner": {"size": 0}})

    with raises(BadRequest) as excinfo:
        reject_invalid_request(None, None, validation.value, None, None)

    assert excinfo.value.description == ("inner.size: Input should be greater than or equal to 1; name: Field required")
