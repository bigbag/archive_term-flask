"""add_paymant_fail

Revision ID: 340b353e2225
Revises: 207c7236773c
Create Date: 2014-10-01 23:08:17.272076

"""

# revision identifiers, used by Alembic.
revision = '340b353e2225'
down_revision = '207c7236773c'

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
        'fail',
        sa.Column('report_id', sa.Integer()),
        sa.Column('count', sa.Integer(), nullable=False, index=True),
        sa.Column('create_timestamp', sa.Integer(), nullable=False),
    )
    op.create_primary_key("pk_fail_report_id", "fail", ["report_id"])


def downgrade_payment():
    op.drop_table("fail")


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
