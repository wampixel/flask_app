from datetime import UTC, datetime, timedelta

from flask import abort, jsonify, request
from sqlalchemy import select

from app.extensions import db
from app.models import SessionModel
from app.utils import get_sha512_hash

IDLE_TIMEOUT = timedelta(minutes=30)


def unauthorized(message: str = "Unauthorized") -> None:
    resp = jsonify(message=message)
    resp.status_code = 401
    abort(resp)


def authenticate() -> None:
    if request.endpoint is None:
        return
    auth = request.headers.get("Authorization", "")
    if not (token := auth.removeprefix("Bearer ").strip() if auth.startswith("Bearer") else ""):
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
