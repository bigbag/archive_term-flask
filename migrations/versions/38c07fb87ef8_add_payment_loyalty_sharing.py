"""add payment_loyalty_sharing

Revision ID: 38c07fb87ef8
Revises: 38b8d8f1026e
Create Date: 2014-09-07 01:19:43.193628

"""

# revision identifiers, used by Alembic.
revision = '38c07fb87ef8'
down_revision = '38b8d8f1026e'

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
        'loyalty_sharing',
        sa.Column('id', sa.Integer()),
        sa.Column('loyalty_id', sa.Integer(), nullable=False, index=True),
        sa.Column('sharing_type', sa.Integer(), nullable=False),
        sa.Column('desc', sa.Text()),
        sa.Column('data', sa.Text()),
        sa.Column('link', sa.Text()),
        sa.Column('control_value', sa.String(256)),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_payment():
    op.drop_table("loyalty_sharing")


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
