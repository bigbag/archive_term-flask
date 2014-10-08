"""add_blacklist_table

Revision ID: 53c2fbd73b89
Revises: 39032327c8d0
Create Date: 2014-10-08 17:50:15.630030

"""

# revision identifiers, used by Alembic.
revision = '53c2fbd73b89'
down_revision = '39032327c8d0'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'blacklist',
        sa.Column('payment_id', sa.String(50), nullable=False),
        sa.Column('timestamp', sa.Integer(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False, index=True, server_default='1'),

    )
    op.create_primary_key("pk_spot_payment_id", "blacklist", ["payment_id"])


def downgrade_term():
    op.drop_table("blacklist")


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
