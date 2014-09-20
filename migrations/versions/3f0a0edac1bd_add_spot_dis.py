"""add spot_dis

Revision ID: 3f0a0edac1bd
Revises: 286f85ea04b
Create Date: 2014-09-07 01:21:30.815379

"""

# revision identifiers, used by Alembic.
revision = '3f0a0edac1bd'
down_revision = '286f85ea04b'

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
        'discodes',
        sa.Column('id', sa.Integer()),
        sa.Column('premium', sa.Integer(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_mobispot():
    op.drop_table("discodes")
