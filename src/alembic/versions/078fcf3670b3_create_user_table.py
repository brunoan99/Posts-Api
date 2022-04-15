"""Create User Table

Revision ID: 078fcf3670b3
Revises: f5c2fb9326f6
Create Date: 2022-04-13 00:35:16.990135

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '078fcf3670b3'
down_revision = 'f5c2fb9326f6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users",
                    sa.Column("id",sa.Integer(), primary_key=True, nullable=False),
                    sa.Column("email", sa.String(), nullable=False, unique=True),
                    sa.Column("password", sa.String(), nullable=False),
                    sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")))


def downgrade():
    op.drop_table("usres")