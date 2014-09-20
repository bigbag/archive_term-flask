"""add term_event

Revision ID: 31625142e74a
Revises: 331a788228b3
Create Date: 2014-09-07 01:22:26.901340

"""

# revision identifiers, used by Alembic.
revision = '31625142e74a'
down_revision = '331a788228b3'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'term_event',
        sa.Column('id', sa.Integer()),
        sa.Column('age', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cost', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('timeout', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('start', sa.String(10), nullable=False, server_default='00:01'),
        sa.Column('stop', sa.String(10), nullable=False, server_default='23:59'),
        sa.Column('min_item', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_item', sa.Integer(), nullable=False, server_default='65535'),
        sa.Column('term_id', sa.Integer(), nullable=False, index=True),
        sa.Column('event_id', sa.Integer(), nullable=False, index=True),
        sa.Column('credit_period', sa.Integer(), nullable=False, server_default='900'),
        sa.Column('credit_amount', sa.Integer(), nullable=False, server_default='50000'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_term():
    op.drop_table("term_event")


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
