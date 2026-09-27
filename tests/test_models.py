import pytest
from flask import Flask

from app.extensions import db
from app.models import TenantModel, UserModel


@pytest.mark.parametrize("blank", ["", "   "])
def test_user_model_rejects_blank_name(app_context: Flask, blank: str) -> None:
    with pytest.raises(ValueError):
        UserModel(name=blank, last_name="Doe")


@pytest.mark.parametrize("blank", ["", "   "])
def test_user_model_rejects_blank_last_name(app_context: Flask, blank: str) -> None:
    with pytest.raises(ValueError):
        UserModel(name="John", last_name=blank)


@pytest.mark.parametrize("blank", ["", "   "])
def test_tenant_model_rejects_blank_name(app_context: Flask, blank: str) -> None:
    with pytest.raises(ValueError):
        TenantModel(name=blank)


def test_user_tenant_relationship_links_to_tenant(app_context: Flask) -> None:
    tenant = TenantModel(name="acme")
    db.session.add(tenant)
    db.session.commit()

    user = UserModel(name="John", last_name="Doe", tenant=tenant)
    db.session.add(user)
    db.session.commit()

    reloaded = db.session.get(UserModel, user.id)
    assert reloaded is not None
    assert reloaded.tenant_id == tenant.id
    assert reloaded.tenant.name == "acme"
