import click
from alembic import command
from alembic.config import Config
from flask import Flask


def register_cli(app: Flask) -> None:
    @app.cli.command("init-db")
    def initialize_database():
        command.upgrade(Config("alembic.ini"), "head")
        click.echo("DB successfully initialized")
