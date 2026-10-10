from flask import Flask
from flask.testing import FlaskClient
from pytest import fixture

from app.extensions import db
from app.models import TenantModel, UserModel
from app.utils import get_argon2_hash

USERS_URL = "/api/v1/users"
PASSWORD = "Changeit"


def add_user(username: str, tenant: TenantModel) -> UserModel:
    user = UserModel(
        username=username, name="John", last_name="Doe", tenant=tenant, passphrase=get_argon2_hash(PASSWORD)
    )
    db.session.add(user)
    return user


@fixture
def caller(app_context: Flask) -> UserModel:
    caller = add_user("jdoe", TenantModel(name="acme"))
    db.session.commit()
    return caller


@fixture
def outsider(caller: UserModel) -> UserModel:
    outsider = add_user("wesker", TenantModel(name="umbrella"))
    db.session.commit()
    return outsider


@fixture
def caller_headers(client: FlaskClient, caller: UserModel) -> dict[str, str]:
    token = client.post("/api/v1/auth/token", auth=(caller.username, PASSWORD)).get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_users_list_only_returns_caller_tenant(
    client: FlaskClient, caller_headers: dict[str, str], outsider: UserModel
) -> None:
    body = client.get(USERS_URL, headers=caller_headers).get_json()
    assert [item["username"] for item in body["items"]] == ["jdoe"]
    assert body["pagination"]["total"] == 1


def test_users_item_returns_user_of_caller_tenant(
    client: FlaskClient, caller_headers: dict[str, str], caller: UserModel
) -> None:
    assert client.get(f"{USERS_URL}/{caller.id}", headers=caller_headers).status_code == 200


def test_users_item_hides_user_of_other_tenant(
    client: FlaskClient, caller_headers: dict[str, str], outsider: UserModel
) -> None:
    assert client.get(f"{USERS_URL}/{outsider.id}", headers=caller_headers).status_code == 404
