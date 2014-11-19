"""add_status_column_in_payment_card

Revision ID: 11de429cd895
Revises: 45422317ee1a
Create Date: 2014-11-17 16:47:28.406010

"""

# revision identifiers, used by Alembic.
revision = '11de429cd895'
down_revision = '45422317ee1a'

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
    op.add_column('payment_card', sa.Column(
        'system', sa.Integer(), nullable=False, server_default='0'))
    op.create_index('ik_payment_card_system', 'payment_card', ['system'])


def downgrade_payment():
    op.drop_column('payment_card', 'system')
    op.drop_index("ik_payment_card_system")


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
