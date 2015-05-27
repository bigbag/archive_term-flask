"""empty message

Revision ID: 5904c7707b91
Revises: 44bbefa9054
Create Date: 2015-05-27 11:42:42.611522

"""

# revision identifiers, used by Alembic.
revision = '5904c7707b91'
down_revision = '44bbefa9054'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.add_column('term', sa.Column(
        'auth', sa.String(16), nullable=False, server_default='pid'))


def downgrade_term():
    op.drop_column('term', 'auth')


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
