"""add firm_term

Revision ID: 226d016d127c
Revises: 51b2b0684fc9
Create Date: 2014-09-07 01:17:58.368034

"""

# revision identifiers, used by Alembic.
revision = '226d016d127c'
down_revision = '51b2b0684fc9'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'firm_term',
        sa.Column('id', sa.Integer()),
        sa.Column('term_id', sa.Integer(), nullable=False, index=True),
        sa.Column('firm_id', sa.Integer(), nullable=False, index=True),
        sa.Column('child_firm_id', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('creation_date', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_term():
    op.drop_table("firm_term")


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
