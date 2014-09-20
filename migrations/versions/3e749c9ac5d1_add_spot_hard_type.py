"""add spot_hard_type

Revision ID: 3e749c9ac5d1
Revises: 3922d2ffe9ee
Create Date: 2014-09-07 01:21:42.830498

"""

# revision identifiers, used by Alembic.
revision = '3e749c9ac5d1'
down_revision = '3922d2ffe9ee'

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
        'spot_hard_type',
        sa.Column('id', sa.Integer()),
        sa.Column('name', sa.Text()),
        sa.Column('hard_id', sa.Integer(), nullable=False),
        sa.Column('color_id', sa.Integer()),
        sa.Column('pattern_id', sa.Integer()),
        sa.Column('show', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('image', sa.String(150), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_mobispot():
    op.drop_table("spot_hard_type")
