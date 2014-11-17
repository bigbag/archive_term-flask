"""add_lock_column_in_payment_fail

Revision ID: 39032327c8d0
Revises: 2513e69619ee
Create Date: 2014-10-02 14:59:38.968462

"""

# revision identifiers, used by Alembic.
revision = '39032327c8d0'
down_revision = '2513e69619ee'

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
    op.add_column('fail', sa.Column(
        'lock', sa.Integer(), nullable=False, server_default='0'))


def downgrade_payment():
    op.drop_column('fail', 'lock')


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
