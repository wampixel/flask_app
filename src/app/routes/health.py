from typing import Self

from flask import Blueprint, Response, jsonify
from flask.views import MethodView
from spectree import Response as SpecResponse

from app.decorators import public
from app.extensions import api
from app.schemas import MessageData

bp = Blueprint("health", __name__, url_prefix="/health")


class Health(MethodView):
    @public
    @api.validate(resp=SpecResponse(HTTP_200=MessageData), tags=["health"], security={})
    def get(self: Self) -> Response:
        """/health"""
        return jsonify(message="healthy service"), 200


bp.add_url_rule("", view_func=Health.as_view("health"))
