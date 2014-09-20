"""add wallet_loyalty

Revision ID: 43c11bf27fed
Revises: 1d387a956397
Create Date: 2014-09-07 01:23:23.965507

"""

# revision identifiers, used by Alembic.
revision = '43c11bf27fed'
down_revision = '1d387a956397'

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
        'wallet_loyalty',
        sa.Column('id', sa.Integer()),
        sa.Column('wallet_id', sa.Integer()),
        sa.Column('loyalty_id', sa.Integer()),
        sa.Column('summ', sa.String(50)),
        sa.Column('count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('part_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('bonus_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('bonus_limit', sa.Integer()),
        sa.Column('checked', sa.Text()),

        sa.Column('status', sa.Integer(), nullable=False, index=True, server_default='0'),
        sa.Column('errors', sa.Text()),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_payment():
    op.drop_table("wallet_loyalty")


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
