"""add payment_card

Revision ID: 48c72f7e0203
Revises: 42afe241c07d
Create Date: 2014-09-07 01:18:51.844206

"""

# revision identifiers, used by Alembic.
revision = '48c72f7e0203'
down_revision = '42afe241c07d'

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
        'payment_card',
        sa.Column('id', sa.Integer()),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('wallet_id', sa.Integer(), nullable=False, index=True),
        sa.Column('pan', sa.String(128), nullable=False),
        sa.Column('token', sa.Text(), nullable=False),
        sa.Column('type', sa.String(128), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_payment():
    op.drop_table("payment_card")


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
