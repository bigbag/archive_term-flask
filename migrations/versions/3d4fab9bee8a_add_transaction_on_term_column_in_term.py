"""empty message

Revision ID: 3d4fab9bee8a
Revises: ('269c57be2c74', '442d0801a90c')
Create Date: 2015-10-21 15:25:12.551648

"""

# revision identifiers, used by Alembic.
revision = '3d4fab9bee8a'
down_revision = ('269c57be2c74', '442d0801a90c')

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.add_column('term', sa.Column(
        'transaction_on_term', sa.Integer(), nullable=True, server_default='0'))


def downgrade_term():
    op.drop_column('term', 'transaction_on_term')


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
