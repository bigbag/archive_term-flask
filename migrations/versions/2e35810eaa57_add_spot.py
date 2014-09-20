"""add spot

Revision ID: 2e35810eaa57
Revises: 1fb9aaa3cb3
Create Date: 2014-09-07 01:21:09.075365

"""

# revision identifiers, used by Alembic.
revision = '2e35810eaa57'
down_revision = '1fb9aaa3cb3'

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
    pass


def downgrade_payment():
    pass


def upgrade_mobispot():
    op.create_table(
        'spot',
        sa.Column('discodes_id', sa.Integer()),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('name', sa.String(300)),
        sa.Column('url', sa.String(150), nullable=False),
        sa.Column('barcode', sa.String(32), nullable=False),
        sa.Column('type', sa.Integer()),
        sa.Column('lang', sa.String(10), nullable=False),
        sa.Column('user_id', sa.Integer()),
        sa.Column('premium', sa.Integer(), nullable=False),
        sa.Column('generated_date', sa.DateTime(), nullable=False),
        sa.Column('registered_date', sa.DateTime()),
        sa.Column('removed_date', sa.DateTime()),
        sa.Column('status', sa.Integer(), nullable=False, index=True),
        sa.Column('code128', sa.String(128), nullable=False),
        sa.Column('hard_type', sa.Integer(), nullable=False),
    )
    op.create_primary_key("pk_spot_discodes_id", "spot", ["discodes_id"])


def downgrade_mobispot():
    op.drop_table("spot")
