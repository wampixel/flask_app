from flask import Blueprint, Flask

from .cli import register_cli
from .configuration import load_configuration
from .extensions import api, db, migrate
from .handlers import register_error_handlers
from .middlewares import authenticate, register_middlewares
from .routes import auth_bp, health_bp, users_bp


def create_app(conf_path: str | None = None) -> Flask:
    configuration = load_configuration(conf_path)

    app = Flask(__name__)
    app.config.from_object(configuration)
    db.init_app(app)
    migrate.init_app(app, db)

    register_cli(app)
    register_error_handlers(app)
    register_middlewares(app)

    v1 = Blueprint("v1", __name__, url_prefix="/api/v1")
    v1.before_request(authenticate)
    v1.register_blueprint(health_bp)
    v1.register_blueprint(auth_bp)
    v1.register_blueprint(users_bp)

    app.register_blueprint(v1)
    api.register(app)

    return app
