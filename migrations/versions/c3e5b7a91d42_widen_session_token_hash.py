"""widen session token hash

Revision ID: c3e5b7a91d42
Revises: a976d5cb3f2d
Create Date: 2026-10-10 10:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c3e5b7a91d42"
down_revision = "a976d5cb3f2d"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("sessions", schema=None) as batch_op:
        batch_op.alter_column(
            "token_hash", existing_type=sa.String(length=64), type_=sa.String(length=128), existing_nullable=False
        )


def downgrade():
    with op.batch_alter_table("sessions", schema=None) as batch_op:
        batch_op.alter_column(
            "token_hash", existing_type=sa.String(length=128), type_=sa.String(length=64), existing_nullable=False
        )
