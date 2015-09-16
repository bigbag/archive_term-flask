"""empty message

Revision ID: 269c57be2c74
Revises: 3921918c588d
Create Date: 2015-09-11 14:50:18.639320

"""

# revision identifiers, used by Alembic.
revision = '269c57be2c74'
down_revision = '3921918c588d'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.add_column('term', sa.Column(
        'update_period', sa.Integer(), nullable=False, server_default='999999999'))
    op.add_column('term', sa.Column(
        'update_force_on_restart', sa.Integer(), nullable=False, server_default='0'))


def downgrade_term():
    op.drop_column('term', 'update_period')
    op.drop_column('term', 'update_force_on_restart')


def upgrade_stack():
    pass


def downgrade_stack():
    pass


def upgrade_payment():
    pass


def downgrade_payment():
    pass


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
