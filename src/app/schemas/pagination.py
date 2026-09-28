from typing import TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParameters(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    pages: int


class Paginated[T](BaseModel):
    items: list[T]
    pagination: PaginationMeta


def paginate(pagination, schemas: type[BaseModel]) -> dict:
    page = Paginated[schemas](
        items=[schemas.model_validate(item) for item in pagination.items],
        pagination=PaginationMeta(
            page=pagination.page, per_page=pagination.per_page, total=pagination.total, pages=pagination.pages
        ),
    )

    return page.model_dump(mode="json")
