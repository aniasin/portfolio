"""empty message

Revision ID: c45c27aec939
Revises: ff156dc60823
Create Date: 2022-11-09 12:14:21.690906

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c45c27aec939'
down_revision = 'ff156dc60823'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('todo_list', 'description',
               existing_type=sa.VARCHAR(length=250),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('todo_list', 'description',
               existing_type=sa.VARCHAR(length=250),
               nullable=False)
    # ### end Alembic commands ###