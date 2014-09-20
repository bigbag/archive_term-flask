"""add payment_wallet

Revision ID: 422b1c860d97
Revises: 38c07fb87ef8
Create Date: 2014-09-07 01:19:54.557662

"""

# revision identifiers, used by Alembic.
revision = '422b1c860d97'
down_revision = '38c07fb87ef8'

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
    op.create_table(
        'wallet',
        sa.Column('id', sa.Integer()),
        sa.Column('payment_id', sa.Integer(), nullable=False),
        sa.Column('hard_id', sa.Integer()),
        sa.Column('name', sa.String(150), nullable=False, server_default=u'My Spot]'),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True, server_default='0'),
        sa.Column('discodes_id', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('creation_date', sa.DateTime(), nullable=False),
        sa.Column('balance', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('type', sa.Integer(), nullable=False, index=True, server_default='1'),
        sa.Column('blacklist', sa.Integer(), nullable=False, index=True, server_default='1'),

        sa.PrimaryKeyConstraint('id')
    )


def downgrade_payment():
    op.drop_table("wallet")


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
