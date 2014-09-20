"""add person

Revision ID: 189e9f074071
Revises: 422b1c860d97
Create Date: 2014-09-07 01:20:08.741773

"""

# revision identifiers, used by Alembic.
revision = '189e9f074071'
down_revision = '422b1c860d97'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'person',
        sa.Column('id', sa.Integer()),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('tabel_id', sa.String(150)),
        sa.Column('birthday', sa.Date()),
        sa.Column('firm_id', sa.Integer(), nullable=False),
        sa.Column('card', sa.String(8)),
        sa.Column('payment_id', sa.String(20), nullable=False, index=True),
        sa.Column('hard_id', sa.String(128), nullable=False),
        sa.Column('creation_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False, index=True, server_default='1'),
        sa.Column('wallet_status', sa.Integer(), nullable=False, index=True, server_default='1'),
        sa.Column('type', sa.Integer(), nullable=False, index=True, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_term():
    op.drop_table("person")


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
