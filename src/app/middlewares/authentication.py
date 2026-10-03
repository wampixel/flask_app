from datetime import UTC, datetime, timedelta

from flask import current_app, request
from sqlalchemy import select

from app.extensions import db
from app.models import SessionModel
from app.utils import get_sha512_hash, unauthorized

IDLE_TIMEOUT = timedelta(minutes=30)


def _is_public_endpoint() -> bool:
    view = current_app.view_functions[request.endpoint]
    if (view_class := getattr(view, "view_class", None)) is None:
        return getattr(view, "is_public", False)

    if (method := request.method.lower()) == "head" and not hasattr(view_class, "head"):
        method = "get"
    handler = getattr(view_class, method, False)
    return getattr(handler, "is_public", False)


def authenticate() -> None:
    if request.endpoint is None or _is_public_endpoint():
        return
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    token = token.strip()
    if scheme.lower() != "bearer" or not token:
        unauthorized()

    now = datetime.now(UTC)
    session = db.session.scalar(
        select(SessionModel).where(
            SessionModel.token_hash == get_sha512_hash(token),
            SessionModel.expires_at > now,
            SessionModel.last_seen_at > now - IDLE_TIMEOUT,
        )
    )

    if not session:
        unauthorized()

    session.last_seen_at = now
    db.session.commit()
