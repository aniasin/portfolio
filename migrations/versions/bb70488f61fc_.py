"""empty message

Revision ID: bb70488f61fc
Revises: 617ae5aae3cf
Create Date: 2022-11-06 12:38:59.077948

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb70488f61fc'
down_revision = '617ae5aae3cf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('to_do_comments')
    op.drop_table('to_do_lists')
    op.drop_table('to_do_priorities')
    op.add_column('todo_list', sa.Column('priority', sa.Integer(), nullable=False))
    op.add_column('todo_list', sa.Column('status', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('todo_list', 'status')
    op.drop_column('todo_list', 'priority')
    op.create_table('to_do_priorities',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=250), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(length=250), autoincrement=False, nullable=False),
    sa.Column('icon', sa.VARCHAR(length=250), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='to_do_priorities_pkey')
    )
    op.create_table('to_do_lists',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('to_do_lists_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('author_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('date', sa.VARCHAR(length=250), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(length=250), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(length=250), autoincrement=False, nullable=False),
    sa.Column('body', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('status', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('priority', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], name='to_do_lists_author_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='to_do_lists_pkey'),
    sa.UniqueConstraint('title', name='to_do_lists_title_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('to_do_comments',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('author_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('to_do_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('text', sa.VARCHAR(length=250), autoincrement=False, nullable=False),
    sa.Column('date', sa.VARCHAR(length=250), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], name='to_do_comments_author_id_fkey'),
    sa.ForeignKeyConstraint(['to_do_id'], ['to_do_lists.id'], name='to_do_comments_to_do_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='to_do_comments_pkey')
    )
    # ### end Alembic commands ###
