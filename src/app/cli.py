import click
from flask import Flask
from flask_migrate import upgrade

from .extensions import db
from .models import TenantModel, UserModel
from .utils import get_argon2_hash

DEFAULT_PASSWORD = "Changeme12345!"


def register_cli(app: Flask) -> None:
    @app.cli.command("init-db")
    def initialize_database() -> None:
        upgrade()
        click.echo("DB successfully initialized")

    @app.cli.command("seed-db")
    def seed() -> None:
        if db.session.query(TenantModel).first() is None:
            db.session.add(TenantModel(name="acme"))
            db.session.add(TenantModel(name="Umbrella corp"))
            db.session.commit()

        if db.session.query(UserModel).first() is None:
            acme = db.session.query(TenantModel).filter_by(name="acme").one()
            umbrella = db.session.query(TenantModel).filter_by(name="Umbrella corp").one()

            db.session.add(
                UserModel(
                    username="jdoe",
                    name="John",
                    last_name="Doe",
                    tenant=acme,
                    passphrase=get_argon2_hash(DEFAULT_PASSWORD),
                )
            )
            db.session.add(
                UserModel(
                    username="jdont",
                    name="John",
                    last_name="Don't",
                    tenant=umbrella,
                    passphrase=get_argon2_hash(DEFAULT_PASSWORD),
                )
            )
            db.session.commit()

        click.echo("DB Seeded")
