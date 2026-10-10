from datetime import UTC, datetime

import pytest
from flask import Flask
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import SessionModel, TenantModel, UserModel
from app.utils import get_argon2_hash, get_sha512_hash


@pytest.mark.parametrize("blank", ["", "   "])
def test_user_model_rejects_blank_name(app_context: Flask, blank: str) -> None:
    with pytest.raises(ValueError):
        UserModel(username="jdoe", name=blank, last_name="Doe", passphrase=get_argon2_hash("changeit"))


@pytest.mark.parametrize("blank", ["", "   "])
def test_user_model_rejects_blank_last_name(app_context: Flask, blank: str) -> None:
    with pytest.raises(ValueError):
        UserModel(username="jdoe", name="John", last_name=blank, passphrase=get_argon2_hash("Changeit"))


@pytest.mark.parametrize("blank", ["", "   "])
def test_user_model_rejects_blank_username(app_context: Flask, blank: str) -> None:
    with pytest.raises(ValueError):
        UserModel(username=blank, name="John", last_name="Doe", passphrase=get_argon2_hash("Changeit"))


@pytest.mark.parametrize("blank", ["", "   "])
def test_user_model_rejects_blank_passphrase(app_context: Flask, blank: str) -> None:
    with pytest.raises(ValueError):
        UserModel(username="jdoe", name="John", last_name="Doe", passphrase=blank)


@pytest.mark.parametrize("blank", ["", "   "])
def test_tenant_model_rejects_blank_name(app_context: Flask, blank: str) -> None:
    with pytest.raises(ValueError):
        TenantModel(name=blank)


def test_user_tenant_relationship_links_to_tenant(app_context: Flask) -> None:
    tenant = TenantModel(name="acme")
    db.session.add(tenant)
    db.session.commit()

    user = UserModel(
        username="jdoe", name="John", last_name="Doe", tenant=tenant, passphrase=get_argon2_hash("Changeit")
    )
    db.session.add(user)
    db.session.commit()

    reloaded = db.session.scalar(select(UserModel).options(joinedload(UserModel.tenant)).where(UserModel.id == user.id))
    assert reloaded is not None
    assert reloaded.tenant_id == tenant.id
    assert reloaded.tenant.name == "acme"


def test_user_password_not_nullable(app_context: Flask) -> None:
    tenant = TenantModel(name="acme")
    db.session.add(tenant)
    db.session.commit()

    user = UserModel(username="jdoe", name="John", last_name="Doe", tenant=tenant)
    db.session.add(user)
    with pytest.raises(ValueError):
        db.session.commit()


def test_deleting_user_removes_its_sessions(app_context: Flask) -> None:
    user = UserModel(
        username="jdoe",
        name="John",
        last_name="Doe",
        tenant=TenantModel(name="acme"),
        passphrase=get_argon2_hash("Changeit"),
    )
    db.session.add(user)
    db.session.commit()
    db.session.add(SessionModel(token_hash=get_sha512_hash("token"), user_id=user.id, expires_at=datetime.now(UTC)))
    db.session.commit()

    db.session.delete(user)
    db.session.commit()

    assert db.session.scalar(select(func.count()).select_from(SessionModel)) == 0
