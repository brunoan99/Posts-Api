"""Create Post Table

Revision ID: f5c2fb9326f6
Revises: 
Create Date: 2022-04-13 00:20:54.570768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5c2fb9326f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("posts", 
                    sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
                    sa.Column("title", sa.String(), nullable=False),
                    sa.Column("content", sa.String(), nullable=False))


def downgrade():
    op.drop_table("posts")
