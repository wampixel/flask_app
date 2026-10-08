from datetime import UTC, datetime
from types import SimpleNamespace

from pydantic import BaseModel

from app.schemas import paginate


class Event(BaseModel):
    at: datetime


def test_paginate_returns_json_ready_values() -> None:
    pagination = SimpleNamespace(
        items=[Event(at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC))], page=1, per_page=20, total=1, pages=1
    )

    assert paginate(pagination, Event) == {
        "items": [{"at": "2026-01-02T03:04:05Z"}],
        "pagination": {"page": 1, "per_page": 20, "total": 1, "pages": 1},
    }
