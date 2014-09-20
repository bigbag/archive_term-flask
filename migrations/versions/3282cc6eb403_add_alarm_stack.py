"""add alarm_stack

Revision ID: 3282cc6eb403
Revises: None
Create Date: 2014-09-06 22:33:29.821671

"""

# revision identifiers, used by Alembic.
revision = '3282cc6eb403'
down_revision = None

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
        'alarm_stack',
        sa.Column('id', sa.Integer()),
        sa.Column('firm_id', sa.Integer(), nullable=False),
        sa.Column('term_id', sa.Integer(), nullable=False),
        sa.Column('emails', sa.Text(), nullable=False),
        sa.Column('interval', sa.Integer(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('lock', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_stack():
    op.drop_table("alarm_stack")


def upgrade_payment():
    pass


def downgrade_payment():
    pass


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
