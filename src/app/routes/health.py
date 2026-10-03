from typing import Self

from flask import Blueprint, Response, jsonify
from flask.views import MethodView

from app.decorators import public

bp = Blueprint("health", __name__, url_prefix="/health")


class Health(MethodView):
    @public
    def get(self: Self) -> Response:
        return jsonify(message="healthy service"), 200


bp.add_url_rule("", view_func=Health.as_view("health"))
