from collections.abc import Iterator
from tempfile import NamedTemporaryFile

from flask import Flask
from pytest import fixture

from app import create_app
from app.extensions import db

DEFAULT_CONFIGURATION = """
force_https={https}
strict_transport_security={https}
provide_automatic_options={automatic_options}


[database]
uri='sqlite:///:memory:'
"""


@fixture
def automatic_options() -> bool:
    return True


@fixture
def https() -> bool:
    return False


@fixture
def app_config_file(https: bool, automatic_options: bool) -> Iterator[str]:
    with NamedTemporaryFile("w", suffix=".toml", encoding="utf-8") as tmp:
        tmp.write(
            DEFAULT_CONFIGURATION.format(https=str(https).lower(), automatic_options=str(automatic_options).lower())
        )
        tmp.flush()
        yield tmp.name


@fixture
def app(app_config_file: str) -> Iterator[Flask]:
    app = create_app(app_config_file)

    yield app

    with app.app_context():
        db.engine.dispose()


@fixture
def client(app):
    return app.test_client()


@fixture
def app_context(app: Flask) -> Iterator[Flask]:
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
