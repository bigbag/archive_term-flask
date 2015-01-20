"""add_wallet_id_column_in_payment_fail_table

Revision ID: 4629ec9a2764
Revises: 2313d9c3b2f6
Create Date: 2015-01-19 21:28:44.370214

"""

# revision identifiers, used by Alembic.
revision = '4629ec9a2764'
down_revision = '2313d9c3b2f6'

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
        'wallet_id', sa.Integer(), nullable=True))


def downgrade_payment():
    op.drop_column('fail', 'wallet_id')


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
