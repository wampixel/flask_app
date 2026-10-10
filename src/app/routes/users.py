from typing import Self

from flask import Blueprint, Response, g, request
from flask.views import MethodView
from spectree import Response as SpecResponse
from sqlalchemy import Select, select

from app.extensions import api, db
from app.models import UserModel
from app.schemas import ErrorData, PaginationParameters, UserData, UsersPage, paginate

bp = Blueprint("users", __name__, url_prefix="/users")


def select_tenant_users() -> Select[tuple[UserModel]]:
    return select(UserModel).where(UserModel.tenant_id == g.current_tenant_id)


class UsersList(MethodView):
    @api.validate(query=PaginationParameters, resp=SpecResponse(HTTP_200=UsersPage, HTTP_401=ErrorData), tags=["users"])
    def get(self: Self) -> Response:
        """/users"""
        query = request.context.query
        stmts = select_tenant_users().order_by(UserModel.id)
        pagination = db.paginate(stmts, page=query.page, per_page=query.per_page, max_per_page=50)
        return paginate(pagination, UserData)


class UsersItem(MethodView):
    @api.validate(resp=SpecResponse(HTTP_200=UserData, HTTP_401=ErrorData, HTTP_404=ErrorData), tags=["users"])
    def get(self: Self, user_id: int) -> UserData:
        """/users/{user_id}"""
        return UserData.model_validate(db.one_or_404(select_tenant_users().where(UserModel.id == user_id)))


bp.add_url_rule("", view_func=UsersList.as_view("list"))
bp.add_url_rule("/<int:user_id>", view_func=UsersItem.as_view("user"))
