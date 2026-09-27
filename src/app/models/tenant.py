from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String

from app.extensions import db


class Tenant(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
