"""add term_user_firm

Revision ID: 37cc2c8fec34
Revises: 53a86c109b36
Create Date: 2014-09-07 01:22:56.324994

"""

# revision identifiers, used by Alembic.
revision = '37cc2c8fec34'
down_revision = '53a86c109b36'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'user_firm',
        sa.Column('id', sa.Integer()),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('firm_id', sa.Integer(), nullable=False, index=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_term():
    op.drop_table("user_firm")


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
