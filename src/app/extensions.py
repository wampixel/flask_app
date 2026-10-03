from importlib.metadata import version
from typing import Any

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from spectree import SecurityScheme, SpecTree
from spectree.models import SecureType, SecuritySchemeData
from spectree.page import PAGE_TEMPLATES
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from app.handlers import reject_invalid_request
from app.schemas import ErrorData

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


db = SQLAlchemy(model_class=Base)
migrate = Migrate()


def has_validated_input(operation: dict[str, Any]) -> bool:
    queried = any(parameter["in"] != "path" for parameter in operation.get("parameters", []))
    return queried or "requestBody" in operation


class ApiSpec(SpecTree):
    def _generate_spec(self) -> dict[str, Any]:
        spec = super()._generate_spec()
        for operations in spec["paths"].values():
            for operation in operations.values():
                if not has_validated_input(operation):
                    operation["responses"].pop(str(self.validation_error_status), None)
        return spec


api = ApiSpec(
    "flask",
    title="flask_app API",
    version=version("app"),
    path="apidoc",
    page_templates={"": PAGE_TEMPLATES["scalar"]},
    security_schemes=[
        SecurityScheme(name="bearer", data=SecuritySchemeData(type=SecureType.HTTP, scheme="bearer")),
        SecurityScheme(name="basic", data=SecuritySchemeData(type=SecureType.HTTP, scheme="basic")),
    ],
    security={"bearer": []},
    validation_error_status=400,
    validation_error_model=ErrorData,
    naming_strategy=lambda model: model.__name__,
    before=reject_invalid_request,
)
