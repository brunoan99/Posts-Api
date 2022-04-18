"""Add created_at and published Columns to Post Table

Revision ID: f919ddc2e6db
Revises: 938d680b4333
Create Date: 2022-04-13 00:46:48.586966

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f919ddc2e6db'
down_revision = '938d680b4333'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts", 
                  sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")))
    op.add_column("posts", 
                  sa.Column("published", sa.Boolean(), server_default="TRUE", nullable=False))


def downgrade():
    op.drop_column("posts", "created_at")
    op.drop_column("posts", "published")
