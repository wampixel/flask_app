from flask import Flask

from app.models import TenantModel, UserModel


def test_seed_db_links_users_to_real_tenants(app_context: Flask) -> None:
    result = app_context.test_cli_runner().invoke(args=["seed-db"])
    assert result.exit_code == 0

    users_by_name = {(u.name, u.last_name): u for u in UserModel.query.all()}
    john_doe = users_by_name[("John", "Doe")]
    john_dont = users_by_name[("John", "Don't")]

    assert john_doe.tenant.name == "acme"
    assert john_dont.tenant.name == "Umbrella corp"
    assert john_doe.tenant_id == TenantModel.query.filter_by(name="acme").one().id


def test_seed_db_is_idempotent(app_context: Flask) -> None:
    runner = app_context.test_cli_runner()
    runner.invoke(args=["seed-db"])
    runner.invoke(args=["seed-db"])

    assert TenantModel.query.count() == 2
    assert UserModel.query.count() == 2
