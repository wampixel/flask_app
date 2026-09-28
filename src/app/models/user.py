from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy.types import String

from app.extensions import db

from .mixins import TenantMixin


class UserModel(TenantMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[int] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    passphrase: Mapped[str] = mapped_column(String(512))

    @validates("name", "last_name", "username", "passphrase")
    def validate_not_blank(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError(f"{key} must not be blank")
        return value


@event.listens_for(UserModel, "before_insert")
def check_required_fields(mapper, connection, target: UserModel) -> None:
    missing = [field for field in ("username", "name", "last_name", "passphrase") if getattr(target, field) is None]
    if missing:
        raise ValueError(f"missing mandatory fields : {', '.join(missing)}")
