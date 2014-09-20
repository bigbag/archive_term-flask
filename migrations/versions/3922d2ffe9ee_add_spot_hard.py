"""add spot_hard

Revision ID: 3922d2ffe9ee
Revises: 3f0a0edac1bd
Create Date: 2014-09-07 01:21:39.078393

"""

# revision identifiers, used by Alembic.
revision = '3922d2ffe9ee'
down_revision = '3f0a0edac1bd'

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
        'spot_hard',
        sa.Column('id', sa.Integer()),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('show', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_mobispot():
    op.drop_table("spot_hard")
