"""add payment_history

Revision ID: 83bc1459603
Revises: 48c72f7e0203
Create Date: 2014-09-07 01:19:01.688807

"""

# revision identifiers, used by Alembic.
revision = '83bc1459603'
down_revision = '48c72f7e0203'

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
        'history',
        sa.Column('id', sa.Integer()),
        sa.Column('report_id', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('wallet_id', sa.Integer(), nullable=False, index=True),
        sa.Column('term_id', sa.Integer(), nullable=False, index=True),
        sa.Column('amount', sa.String(50), nullable=False),
        sa.Column('creation_date', sa.DateTime, nullable=False),
        sa.Column('request_id', sa.Text(), nullable=False),
        sa.Column('invoice_id', sa.Text()),
        sa.Column('type', sa.Integer(), nullable=False, index=True, server_default='1'),
        sa.Column('status', sa.Integer(), nullable=False, index=True, server_default='0'),
    )


def downgrade_payment():
    op.drop_table("history")


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
