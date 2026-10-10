from flask import Flask
from sqlalchemy.orm import joinedload

from app.models import TenantModel, UserModel
from app.utils.crypto import check_argon2_hash

SEED_ARGS = ["seed-db", "--password", "demo-password"]


def test_seed_db_links_users_to_real_tenants(app_context: Flask) -> None:
    result = app_context.test_cli_runner().invoke(args=SEED_ARGS)
    assert result.exit_code == 0

    users_by_name = {(u.name, u.last_name): u for u in UserModel.query.options(joinedload(UserModel.tenant)).all()}
    john_doe = users_by_name[("John", "Doe")]
    john_dont = users_by_name[("John", "Don't")]

    assert john_doe.tenant.name == "acme"
    assert john_dont.tenant.name == "Umbrella corp"
    assert john_doe.tenant_id == TenantModel.query.filter_by(name="acme").one().id


def test_seed_db_is_idempotent(app_context: Flask) -> None:
    runner = app_context.test_cli_runner()
    runner.invoke(args=SEED_ARGS)
    runner.invoke(args=SEED_ARGS)

    assert TenantModel.query.count() == 2
    assert UserModel.query.count() == 2


def test_seed_db_hashes_the_given_password(app_context: Flask) -> None:
    app_context.test_cli_runner().invoke(args=SEED_ARGS)

    assert all(check_argon2_hash(user.passphrase, "demo-password") for user in UserModel.query.all())
