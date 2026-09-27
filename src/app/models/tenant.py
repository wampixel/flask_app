from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy.types import String

from app.extensions import db


class TenantModel(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))

    @validates("name")
    def validate_not_blank(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError(f"{key} must not be blank")
        return value
