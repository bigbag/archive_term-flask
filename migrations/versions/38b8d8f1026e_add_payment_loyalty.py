"""add payment_loyalty

Revision ID: 38b8d8f1026e
Revises: 10a969ae3768
Create Date: 2014-09-07 01:19:32.894037

"""

# revision identifiers, used by Alembic.
revision = '38b8d8f1026e'
down_revision = '83bc1459603'

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
        'loyalty',
        sa.Column('id', sa.Integer()),
        sa.Column('name', sa.String(128)),
        sa.Column('desc', sa.Text()),
        sa.Column('terms_id', sa.Text()),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('firm_id', sa.Integer(), nullable=False),
        sa.Column('rules', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('interval', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('amount', sa.String(32), nullable=False, server_default='0'),
        sa.Column('threshold', sa.String(32), nullable=False, server_default='0'),
        sa.Column('creation_date', sa.DateTime(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('stop_date', sa.DateTime(), nullable=False),
        sa.Column('img', sa.Text(), nullable=False),
        sa.Column('part_limit', sa.Integer()),
        sa.Column('sharing_type', sa.Integer()),
        sa.Column('data', sa.Text()),
        sa.Column('coupon_class', sa.String(64), nullable=False),
        sa.Column('target_url', sa.Text()),
        sa.Column('limit', sa.Integer()),
        sa.Column('timeout', sa.Integer()),
        sa.Column('bonus_count', sa.Integer()),
        sa.Column('bonus_limit', sa.Integer()),
        sa.Column('soc_block', sa.Text()),
        sa.Column('link', sa.Text()),
        sa.Column('control_value', sa.String(256)),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_payment():
    op.drop_table("loyalty")


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
