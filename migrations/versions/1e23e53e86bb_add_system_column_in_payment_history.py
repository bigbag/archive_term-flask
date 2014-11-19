"""add_system_column_in_payment_history

Revision ID: 1e23e53e86bb
Revises: 11de429cd895
Create Date: 2014-11-17 18:06:13.179893

"""

# revision identifiers, used by Alembic.
revision = '1e23e53e86bb'
down_revision = '11de429cd895'

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
    op.add_column('history', sa.Column(
        'system', sa.Integer(), nullable=False, server_default='0'))
    op.create_index('ik_history_system', 'history', ['system'])


def downgrade_payment():
    op.drop_column('history', 'system')
    op.drop_index("ik_history_system")


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
