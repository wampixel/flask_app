from flask import Blueprint, Response
from flask.views import MethodView
from typing import Self

from flask import jsonify

bp = Blueprint("health", __name__, url_prefix="/health")

@bp.before_request
def before() -> None:
    print("verify auth for example")

class Health(MethodView):
    def get(self: Self) -> Response:
        return jsonify(
            message="healthy service"
        ), 200

bp.add_url_rule("/", view_func=Health.as_view('health'))