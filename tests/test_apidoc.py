from flask import Flask
from flask.testing import FlaskClient
from pytest import fixture, mark

from app.extensions import db
from app.models import TenantModel, UserModel
from app.utils import get_argon2_hash

PASSWORD = "Changeit"


@fixture
def user(app_context: Flask) -> UserModel:
    tenant = TenantModel(name="acme")
    db.session.add(tenant)
    user = UserModel(username="jdoe", name="John", last_name="Doe", tenant=tenant, passphrase=get_argon2_hash(PASSWORD))
    db.session.add(user)
    db.session.add(
        UserModel(username="jdont", name="John", last_name="Dont", tenant=tenant, passphrase=get_argon2_hash(PASSWORD))
    )
    db.session.commit()
    return user


@fixture
def auth_headers(client: FlaskClient, user: UserModel) -> dict[str, str]:
    resp = client.post("/api/v1/auth/token", auth=(user.username, PASSWORD))
    assert resp.status_code == 201
    return {"Authorization": f"Bearer {resp.get_json()['access_token']}"}


def test_spec_is_public_and_lists_every_route(client: FlaskClient) -> None:
    resp = client.get("/apidoc/openapi.json")
    assert resp.status_code == 200
    assert set(resp.get_json()["paths"]) == {
        "/api/v1/health",
        "/api/v1/auth/token",
        "/api/v1/users",
        "/api/v1/users/{user_id}",
    }


def test_spec_gives_every_operation_a_summary(client: FlaskClient) -> None:
    paths = client.get("/apidoc/openapi.json").get_json()["paths"]
    fallbacks = [
        f"{method.upper()} {path}"
        for path, operations in paths.items()
        for method, operation in operations.items()
        if operation["summary"].endswith(f"<{method.upper()}>")
    ]
    assert fallbacks == []


def test_spec_marks_public_routes_without_bearer(client: FlaskClient) -> None:
    spec = client.get("/apidoc/openapi.json").get_json()
    assert spec["security"] == [{"bearer": []}]
    assert spec["paths"]["/api/v1/health"]["get"]["security"] == []
    assert spec["paths"]["/api/v1/auth/token"]["post"]["security"] == [{"basic": []}]


@mark.parametrize("headers", [{}, {"Authorization": "Bearer nope"}], ids=["missing", "invalid"])
def test_protected_route_rejects_with_error_data(
    client: FlaskClient, app_context: Flask, headers: dict[str, str]
) -> None:
    resp = client.get("/api/v1/users", headers=headers)
    assert resp.status_code == 401
    assert resp.get_json()["type"] == "unauthorized"


def test_token_rejects_bad_credentials_with_error_data(client: FlaskClient, user: UserModel) -> None:
    resp = client.post("/api/v1/auth/token", auth=(user.username, "wrong"))
    assert resp.status_code == 401
    assert resp.get_json()["type"] == "unauthorized"


def test_spec_documents_400_only_on_routes_with_input(client: FlaskClient) -> None:
    paths = client.get("/apidoc/openapi.json").get_json()["paths"]
    assert "400" in paths["/api/v1/users"]["get"]["responses"]
    assert "400" not in paths["/api/v1/health"]["get"]["responses"]
    assert "400" not in paths["/api/v1/users/{user_id}"]["get"]["responses"]


def test_scalar_is_the_only_reader(client: FlaskClient) -> None:
    resp = client.get("/apidoc", follow_redirects=True)
    assert resp.status_code == 200
    assert b"openapi.json" in resp.data
    assert client.get("/apidoc/swagger", follow_redirects=True).status_code == 404


def test_public_routes_stay_reachable_without_token(client: FlaskClient, user: UserModel) -> None:
    assert client.get("/api/v1/health").status_code == 200
    assert client.post("/api/v1/auth/token", auth=(user.username, PASSWORD)).status_code == 201


@mark.parametrize("query", ["per_page=0", "per_page=51", "page=0", "page=abc"])
def test_users_list_rejects_invalid_pagination(client: FlaskClient, auth_headers: dict[str, str], query: str) -> None:
    resp = client.get(f"/api/v1/users?{query}", headers=auth_headers)
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["code"] == 400
    assert body["type"] == "bad_request"
    assert body["message"].startswith(query.split("=")[0])


def test_spec_documents_errors_with_error_data(client: FlaskClient) -> None:
    responses = client.get("/apidoc/openapi.json").get_json()["paths"]["/api/v1/users"]["get"]["responses"]
    for status in ("400", "401"):
        assert responses[status]["content"]["application/json"]["schema"]["$ref"] == "#/components/schemas/ErrorData"


def test_users_list_paginates(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    body = client.get("/api/v1/users?page=2&per_page=1", headers=auth_headers).get_json()
    assert [item["username"] for item in body["items"]] == ["jdont"]
    assert body["pagination"] == {"page": 2, "per_page": 1, "total": 2, "pages": 2}


def test_users_item_returns_user_data(client: FlaskClient, auth_headers: dict[str, str], user: UserModel) -> None:
    resp = client.get(f"/api/v1/users/{user.id}", headers=auth_headers)
    assert resp.get_json() == {"id": user.id, "name": "John", "last_name": "Doe", "username": "jdoe"}
