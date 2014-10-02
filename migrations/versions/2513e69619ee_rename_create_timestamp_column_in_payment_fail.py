"""rename_create_timestamp_columt

Revision ID: 2513e69619ee
Revises: 340b353e2225
Create Date: 2014-10-02 14:59:13.350111

"""

# revision identifiers, used by Alembic.
revision = '2513e69619ee'
down_revision = '340b353e2225'

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
    op.alter_column('fail', 'create_timestamp',
                    existing_type=sa.Integer(), new_column_name='timestamp')


def downgrade_payment():
    op.alter_column('fail', 'timestamp',
                    existing_type=sa.Integer(), new_column_name='create_timestamp')


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
