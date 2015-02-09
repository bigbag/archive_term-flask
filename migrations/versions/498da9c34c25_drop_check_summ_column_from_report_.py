"""drop_check_summ_column_from_report_stack_table

Revision ID: 498da9c34c25
Revises: 2ac9199896f6
Create Date: 2015-02-05 13:12:46.019494

"""

# revision identifiers, used by Alembic.
revision = '498da9c34c25'
down_revision = '2ac9199896f6'

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
    op.drop_column('report_stack', 'check_summ')


def downgrade_stack():
    op.add_column('report_stack', sa.Column(
        'check_summ', sa.Text(), nullable=True))


def upgrade_payment():
    pass


def downgrade_payment():
    pass


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
