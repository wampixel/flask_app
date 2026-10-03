from typing import Self

from flask import Blueprint, Response, jsonify

from app.views import ApiView

bp = Blueprint("health", __name__, url_prefix="/health")


class Health(ApiView):
    def get(self: Self) -> Response:
        return jsonify(message="healthy service"), 200


bp.add_url_rule("/", view_func=Health.as_view("health"))
