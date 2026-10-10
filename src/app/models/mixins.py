from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from .tenant import TenantModel


class TenantMixin:
    @declared_attr
    def tenant_id(cls) -> Mapped[int]:
        return mapped_column(ForeignKey(TenantModel.id), nullable=False, index=True)

    @declared_attr
    def tenant(cls) -> Mapped[TenantModel]:
        return relationship(TenantModel, lazy="raise")
