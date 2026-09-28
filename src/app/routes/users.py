from typing import Self

from flask import Blueprint, Response, abort, jsonify, request
from flask.views import MethodView
from sqlalchemy import select

from app.extensions import db
from app.middlewares import authenticate
from app.models import UserModel
from app.schemas import UserData, paginate

bp = Blueprint("users", __name__, url_prefix="/users")
bp.before_request(authenticate)


class UsersList(MethodView):
    def get(self: Self) -> Response:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        if page < 1 or per_page < 1:
            abort(400, description="page et per_page doivent être des entiers positifs")

        stmts = select(UserModel).order_by(UserModel.id)
        pagination = db.paginate(stmts, page=page, per_page=per_page, max_per_page=50)
        return paginate(pagination, UserData)


class UsersItem(MethodView):
    def get(self: Self, user_id: int) -> Response:
        user = db.get_or_404(UserModel, user_id)

        return jsonify(name=user.name, last_name=user.last_name, username=user.username)


bp.add_url_rule("/", view_func=UsersList.as_view("list"))
bp.add_url_rule("/<int:user_id>", view_func=UsersItem.as_view("user"))
