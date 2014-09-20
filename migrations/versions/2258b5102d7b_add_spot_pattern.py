"""add spot_pattern

Revision ID: 2258b5102d7b
Revises: 3e749c9ac5d1
Create Date: 2014-09-07 01:21:57.047242

"""

# revision identifiers, used by Alembic.
revision = '2258b5102d7b'
down_revision = '3e749c9ac5d1'

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
    pass


def downgrade_stack():
    pass


def upgrade_payment():
    pass


def downgrade_payment():
    pass


def upgrade_mobispot():
    op.create_table(
        'spot_pattern',
        sa.Column('id', sa.Integer()),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('show', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_mobispot():
    op.drop_table("spot_pattern")
