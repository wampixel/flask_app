from importlib.metadata import version

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from spectree import SecurityScheme
from spectree.models import SecureType, SecuritySchemeData
from spectree.page import PAGE_TEMPLATES

from app.database import Base
from app.documentation import ApiSpec
from app.handlers import reject_invalid_request
from app.schemas import ErrorData

db = SQLAlchemy(model_class=Base)
migrate = Migrate()

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
