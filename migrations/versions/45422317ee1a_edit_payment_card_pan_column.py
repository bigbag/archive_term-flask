"""empty message

Revision ID: 45422317ee1a
Revises: 31c8c264892c
Create Date: 2014-11-15 18:15:48.450466

"""

# revision identifiers, used by Alembic.
revision = '45422317ee1a'
down_revision = '31c8c264892c'

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
    op.alter_column('payment_card', 'pan',
                    existing_type=sa.String(128), nullable=True)


def downgrade_payment():
    op.alter_column('payment_card', 'pan',
                    existing_type=sa.String(128), nullable=False)


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
