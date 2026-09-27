from collections.abc import Iterator
from tempfile import NamedTemporaryFile

from flask import Flask
from pytest import fixture

from app import create_app
from app.extensions import db

DEFAULT_CONFIGURATION = """
env = 'dev'

[database]
uri='sqlite:///:memory:'
"""


@fixture
def app_config_file() -> Iterator[str]:
    with NamedTemporaryFile("w", suffix=".toml", encoding="utf-8") as tmp:
        tmp.write(DEFAULT_CONFIGURATION)
        tmp.flush()
        yield tmp.name


@fixture
def app(app_config_file: str):
    app = create_app(app_config_file)

    yield app


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
