"""empty message

Revision ID: ff156dc60823
Revises: d508bc2fdf23
Create Date: 2022-11-09 12:11:47.571002

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff156dc60823'
down_revision = 'd508bc2fdf23'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('todo_list', 'body',
               existing_type=sa.TEXT(),
               nullable=True)
    op.drop_column('todo_list', 'icon')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todo_list', sa.Column('icon', sa.VARCHAR(length=250), autoincrement=False, nullable=True))
    op.alter_column('todo_list', 'body',
               existing_type=sa.TEXT(),
               nullable=False)
    # ### end Alembic commands ###
