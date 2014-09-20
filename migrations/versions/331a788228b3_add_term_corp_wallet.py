"""add term_corp_wallet

Revision ID: 331a788228b3
Revises: 474560d8811d
Create Date: 2014-09-07 01:22:18.179706

"""

# revision identifiers, used by Alembic.
revision = '331a788228b3'
down_revision = '474560d8811d'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'corp_wallet',
        sa.Column('id', sa.Integer()),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('creation_date', sa.DateTime(), nullable=False),
        sa.Column('balance', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('limit', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('interval', sa.Integer(), nullable=False, index=True, server_default='0'),
        sa.Column('status', sa.Integer(), nullable=False, index=True, server_default='1'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_term():
    op.drop_table("corp_wallet")


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
