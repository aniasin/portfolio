"""empty message

Revision ID: d508bc2fdf23
Revises: 5348c4138186
Create Date: 2022-11-08 10:39:40.026994

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd508bc2fdf23'
down_revision = '5348c4138186'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todo_projects', sa.Column('author_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'todo_projects', 'users', ['author_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'todo_projects', type_='foreignkey')
    op.drop_column('todo_projects', 'author_id')
    # ### end Alembic commands ###