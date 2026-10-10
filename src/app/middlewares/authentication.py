from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import NoReturn

from flask import abort, current_app, g, request
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import SessionModel
from app.utils import get_sha512_hash

BEARER_SCHEME = "Bearer"
IDLE_TIMEOUT = timedelta(minutes=30)


def public[F: Callable[..., object]](func: F) -> F:
    func.is_public = True
    return func


def unauthorized() -> NoReturn:
    abort(401)


def _is_public_endpoint() -> bool:
    view_class = getattr(current_app.view_functions[request.endpoint], "view_class", None)
    if (method := request.method.lower()) == "head" and not hasattr(view_class, "head"):
        method = "get"
    handler = getattr(view_class, method, False)
    return getattr(handler, "is_public", False)


def _is_automatic_options() -> bool:
    return request.method == "OPTIONS" and request.url_rule.provide_automatic_options


def authenticate() -> None:
    if request.endpoint is None or _is_automatic_options() or _is_public_endpoint():
        return
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    token = token.strip()
    if scheme.lower() != BEARER_SCHEME.lower() or not token:
        unauthorized()

    now = datetime.now(UTC)
    session = db.session.scalar(
        select(SessionModel)
        .options(joinedload(SessionModel.user, innerjoin=True))
        .where(
            SessionModel.token_hash == get_sha512_hash(token),
            SessionModel.expires_at > now,
            SessionModel.last_seen_at > now - IDLE_TIMEOUT,
        )
    )

    if not session:
        unauthorized()

    g.current_tenant_id = session.user.tenant_id
    session.last_seen_at = now
    db.session.commit()
