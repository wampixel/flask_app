from datetime import UTC, datetime, timedelta, tzinfo

from flask import Blueprint, Flask
from flask.testing import FlaskClient
from flask.views import MethodView
from pytest import MonkeyPatch, fixture, mark

from app.extensions import db
from app.middlewares import authenticate, public
from app.middlewares.authentication import IDLE_TIMEOUT
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


def set_session(**values: datetime) -> None:
    session = db.session.scalar(db.select(SessionModel))
    for field, value in values.items():
        setattr(session, field, value)
    db.session.commit()


def shift_session(**changes: timedelta) -> None:
    set_session(**{field: datetime.now(UTC) + delta for field, delta in changes.items()})


@fixture
def frozen_now(monkeypatch: MonkeyPatch) -> datetime:
    now = datetime.now(UTC).replace(microsecond=0)

    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz: tzinfo | None = None) -> datetime:
            return now

    monkeypatch.setattr("app.middlewares.authentication.datetime", FrozenDatetime)
    return now


class HeadProtectedView(MethodView):
    @public
    def get(self) -> str:
        return "public"

    def head(self) -> str:
        return ""


def function_view() -> str:
    return "function"


@fixture
def probe(app: Flask) -> None:
    probe = Blueprint("probe", __name__, url_prefix="/probe")
    probe.before_request(authenticate)
    probe.add_url_rule("/head", view_func=HeadProtectedView.as_view("head_protected"))
    probe.add_url_rule("/function", view_func=function_view)
    app.register_blueprint(probe)


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


def test_protected_route_rejects_session_expiring_now(client: FlaskClient, token: str, frozen_now: datetime) -> None:
    set_session(expires_at=frozen_now)
    assert client.get(USERS_URL, headers=bearer(token)).status_code == 401


def test_protected_route_rejects_session_idle_for_exactly_the_timeout(
    client: FlaskClient, token: str, frozen_now: datetime
) -> None:
    set_session(last_seen_at=frozen_now - IDLE_TIMEOUT)
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


def test_own_head_method_ignores_public_get(client: FlaskClient, probe: None) -> None:
    assert client.get("/probe/head").status_code == 200
    assert client.head("/probe/head").status_code == 401


def test_function_view_requires_token(client: FlaskClient, probe: None) -> None:
    assert client.get("/probe/function").status_code == 401


def test_token_rejects_wrong_passphrase(client: FlaskClient, user: UserModel) -> None:
    assert client.post(TOKEN_URL, auth=("jdoe", "wrong")).status_code == 401


def test_token_rejects_missing_credentials(client: FlaskClient, user: UserModel) -> None:
    assert client.post(TOKEN_URL).status_code == 401
