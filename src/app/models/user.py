from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String

from app.extensions import db

from .mixins import TenantMixin


class UserModel(TenantMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
