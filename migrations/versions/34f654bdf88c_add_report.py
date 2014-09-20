"""add report

Revision ID: 34f654bdf88c
Revises: 33d1d88987a7
Create Date: 2014-09-07 01:20:35.417046

"""

# revision identifiers, used by Alembic.
revision = '34f654bdf88c'
down_revision = '33d1d88987a7'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'report',
        sa.Column('id', sa.Integer()),
        sa.Column('term_id', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('payment_id', sa.String(20), nullable=False, server_default='0'),
        sa.Column('term_firm_id', sa.Integer(), nullable=False, index=True),
        sa.Column('person_firm_id', sa.Integer(), nullable=False, index=True, server_default='0'),
        sa.Column('amount', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('corp_type', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('type', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('creation_date', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_term():
    op.drop_table("report")


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
