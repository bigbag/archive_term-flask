"""add likes_stack

Revision ID: 3324739f958a
Revises: 226d016d127c
Create Date: 2014-09-07 01:18:18.856319

"""

# revision identifiers, used by Alembic.
revision = '3324739f958a'
down_revision = '226d016d127c'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    pass


def downgrade_term():
    pass


def upgrade_stack():
    op.create_table(
        'likes_stack',
        sa.Column('id', sa.Integer()),
        sa.Column('token_id', sa.Integer()),
        sa.Column('loyalty_id', sa.Integer(), nullable=False),
        sa.Column('sharing_id', sa.Integer(), nullable=False),
        sa.Column('lock', sa.Integer(), nullable=False, index=True, server_default='0'),
        sa.Column('wl_id', sa.Integer()),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_stack():
    op.drop_table("likes_stack")


def upgrade_payment():
    pass


def downgrade_payment():
    pass


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
