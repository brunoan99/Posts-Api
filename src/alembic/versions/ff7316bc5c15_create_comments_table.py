"""Create Comments Table

Revision ID: ff7316bc5c15
Revises: f919ddc2e6db
Create Date: 2022-04-13 01:00:43.627308

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff7316bc5c15'
down_revision = 'f919ddc2e6db'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("comments",
                sa.Column("id",sa.Integer(), primary_key=True, nullable=False),
                sa.Column("content", sa.String(), nullable=False, unique=True),
                sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
                sa.Column("post_id", sa.Integer(), nullable=False),
                sa.Column("owner_id", sa.Integer(), nullable=False))
    op.create_foreign_key("commnents_posts_fk", source_table="comments", referent_table="posts", local_cols=["post_id"], remote_cols=["id"], ondelete="CASCADE")
    op.create_foreign_key("commnents_users_fk", source_table="comments", referent_table="users", local_cols=["owner_id"], remote_cols=["id"], ondelete="CASCADE")


def downgrade():
    op.drop_table("comments")
