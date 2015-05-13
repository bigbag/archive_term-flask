"""empty message

Revision ID: 44bbefa9054
Revises: 38a38b8ff31a
Create Date: 2015-05-13 16:38:11.235187

"""

# revision identifiers, used by Alembic.
revision = '44bbefa9054'
down_revision = '38a38b8ff31a'

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
    pass


def downgrade_payment():
    pass


def upgrade_mobispot():
    op.create_table(
        'spot_troika',
        sa.Column('discodes_id', sa.Integer()),
    )
    op.create_primary_key("pk_spot_troika_discodes_id", "spot_troika", ["discodes_id"])


def downgrade_mobispot():
    op.drop_table("spot_troika")
