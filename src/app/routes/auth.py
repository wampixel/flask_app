from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from typing import Self

from flask import Blueprint, Response, jsonify, request
from flask.views import MethodView
from spectree import Response as SpecResponse
from sqlalchemy import delete, or_, select

from app.extensions import api, db
from app.middlewares import BEARER_SCHEME, public, unauthorized
from app.models import SessionModel, UserModel
from app.schemas import ErrorData, TokenData
from app.utils import check_argon2_hash, get_sha512_hash

bp = Blueprint("auth", __name__, url_prefix="/auth")


class Token(MethodView):
    @public
    @api.validate(resp=SpecResponse(HTTP_201=TokenData, HTTP_401=ErrorData), tags=["auth"], security={"basic": []})
    def post(self: Self) -> Response:
        """/auth/token"""
        creds = request.authorization
        if creds is None or creds.type != "basic" or not creds.username or not creds.password:
            unauthorized()

        user: UserModel = db.session.scalar(
            select(UserModel).where(UserModel.username == creds.username.strip().lower())
        )
        if not check_argon2_hash(user.passphrase if user else None, creds.password):
            unauthorized()

        now = datetime.now(UTC)
        idle_timeout = timedelta(hours=8)

        db.session.execute(
            delete(SessionModel).where(
                SessionModel.user_id == user.id,
                or_(SessionModel.expires_at <= now, SessionModel.last_seen_at <= now - idle_timeout),
            )
        )

        token = token_urlsafe(32)
        session = SessionModel(
            token_hash=get_sha512_hash(token),
            user_id=user.id,
            created_at=now,
            last_seen_at=now,
            expires_at=now + idle_timeout,
        )
        db.session.add(session)
        db.session.commit()

        resp = jsonify(
            {
                "access_token": token,
                "token_type": BEARER_SCHEME,
                "expires_at": session.expires_at.isoformat(),
            }
        )
        resp.status_code = 201
        resp.headers["Cache-Control"] = "no-store"

        return resp


bp.add_url_rule("/token", view_func=Token.as_view("token"))
