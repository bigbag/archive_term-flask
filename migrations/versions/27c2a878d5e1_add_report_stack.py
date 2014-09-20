"""add report_stack

Revision ID: 27c2a878d5e1
Revises: 34f654bdf88c
Create Date: 2014-09-07 01:20:49.136181

"""

# revision identifiers, used by Alembic.
revision = '27c2a878d5e1'
down_revision = '34f654bdf88c'

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
    op.create_table(
        'report_stack',
        sa.Column('id', sa.Integer()),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('firm_id', sa.Integer(), nullable=False, index=True),
        sa.Column('emails', sa.Text(), nullable=False),
        sa.Column('excel', sa.Integer(), nullable=False),
        sa.Column('type', sa.Integer(), nullable=False, index=True),
        sa.Column('interval', sa.Integer(), nullable=False),
        sa.Column('details', sa.Text()),
        sa.Column('launch_date', sa.DateTime()),
        sa.Column('check_summ', sa.Text(), nullable=False),
        sa.Column('lock', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_stack():
    op.drop_table("report_stack")


def upgrade_payment():
    pass


def downgrade_payment():
    pass


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
