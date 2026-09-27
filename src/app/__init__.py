from flask import Blueprint, Flask

from .cli import register_cli
from .configuration import load_configuration
from .extensions import db
from .handlers.errors import register_error_handlers
from .routes import health, users


def create_app() -> Flask:
    configuration = load_configuration()

    app = Flask(__name__)
    app.config.from_object(configuration)
    db.init_app(app)

    register_cli(app)
    register_error_handlers(app)

    v1 = Blueprint("v1", __name__, url_prefix="/api/v1")
    v1.register_blueprint(health.bp)
    v1.register_blueprint(users.bp)

    app.register_blueprint(v1)

    return app
