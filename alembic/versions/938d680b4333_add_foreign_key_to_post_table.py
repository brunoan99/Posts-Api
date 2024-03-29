"""ADD Foreign-key to Post Table

Revision ID: 938d680b4333
Revises: 078fcf3670b3
Create Date: 2022-04-13 00:42:09.651761

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '938d680b4333'
down_revision = '078fcf3670b3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts",
                  sa.Column("owner_id", sa.Integer(), nullable=False))
    op.create_foreign_key("posts_users_fk", source_table="posts", referent_table="users", local_cols=["owner_id"], remote_cols=["id"], ondelete="CASCADE")



def downgrade():
    op.drop_constraint("posts_users_fk", table_name="posts")
    op.drop_column("posts", "owner_id")
