from datetime import UTC, datetime, timedelta

from flask import Flask
from flask.testing import FlaskClient
from pytest import fixture, mark

from app.extensions import db
from app.models import SessionModel, TenantModel, UserModel
from app.utils import get_argon2_hash

USERS_URL = "/api/v1/users"
TOKEN_URL = "/api/v1/auth/token"


@fixture
def user(app_context: Flask) -> UserModel:
    tenant = TenantModel(name="acme")
    user = UserModel(
        username="jdoe", name="John", last_name="Doe", passphrase=get_argon2_hash("changeit"), tenant=tenant
    )
    db.session.add(user)
    db.session.commit()
    return user


@fixture
def token(client: FlaskClient, user: UserModel) -> str:
    return client.post(TOKEN_URL, auth=("jdoe", "changeit")).get_json()["access_token"]


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def shift_session(**changes: timedelta) -> None:
    session = db.session.scalar(db.select(SessionModel))
    for field, delta in changes.items():
        setattr(session, field, datetime.now(UTC) + delta)
    db.session.commit()


def test_token_grants_access_to_protected_route(client: FlaskClient, token: str) -> None:
    assert client.get(USERS_URL, headers=bearer(token)).status_code == 200


def test_protected_route_rejects_missing_token(client: FlaskClient, user: UserModel) -> None:
    assert client.get(USERS_URL).status_code == 401


def test_protected_route_rejects_unknown_token(client: FlaskClient, token: str) -> None:
    assert client.get(USERS_URL, headers=bearer("unknown")).status_code == 401


def test_protected_route_rejects_valid_token_with_wrong_scheme(client: FlaskClient, token: str) -> None:
    assert client.get(USERS_URL, headers={"Authorization": f"Basic {token}"}).status_code == 401


def test_protected_route_accepts_extra_spaces_around_token(client: FlaskClient, token: str) -> None:
    assert client.get(USERS_URL, headers={"Authorization": f"bearer   {token}  "}).status_code == 200


def test_protected_route_rejects_expired_session(client: FlaskClient, token: str) -> None:
    shift_session(expires_at=-timedelta(seconds=1))
    assert client.get(USERS_URL, headers=bearer(token)).status_code == 401


def test_protected_route_rejects_idle_session(client: FlaskClient, token: str) -> None:
    shift_session(last_seen_at=-timedelta(minutes=31))
    assert client.get(USERS_URL, headers=bearer(token)).status_code == 401


@mark.parametrize("automatic_options", [True])
def test_automatic_options_answers_without_token(client: FlaskClient) -> None:
    resp = client.options(USERS_URL)
    assert resp.status_code == 200
    assert "GET" in resp.headers["Allow"]


@mark.parametrize("automatic_options", [False])
def test_disabled_automatic_options_rejects_options(client: FlaskClient) -> None:
    assert client.options(USERS_URL).status_code == 405


def test_public_route_accepts_head_without_token(client: FlaskClient) -> None:
    assert client.head("/api/v1/health").status_code == 200


def test_token_rejects_wrong_passphrase(client: FlaskClient, user: UserModel) -> None:
    assert client.post(TOKEN_URL, auth=("jdoe", "wrong")).status_code == 401


def test_token_rejects_missing_credentials(client: FlaskClient, user: UserModel) -> None:
    assert client.post(TOKEN_URL).status_code == 401
