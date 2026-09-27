from typing import Self

from flask import Blueprint, Response, abort, jsonify
from flask.views import MethodView

bp = Blueprint("users", __name__, url_prefix="/users")

USERS = [
    {"first": "Benoit", "last": "Cabaillet"},
    {"first": "Tristan", "last": "Rodrigo"},
]


class UsersList(MethodView):
    def get(self: Self) -> Response:
        return jsonify(
            users=USERS,
        ), 200


class UsersItem(MethodView):
    def get(self: Self, user_id: int) -> Response:
        print(user_id)
        if user_id > len(USERS):
            abort(404, description="Resource not found")
        return jsonify(USERS[user_id - 1])


bp.add_url_rule("/", view_func=UsersList.as_view("list"))
bp.add_url_rule("/<int:user_id>", view_func=UsersItem.as_view("user"))
