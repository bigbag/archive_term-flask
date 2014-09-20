"""add event_type

Revision ID: 1aa2a2ddbd71
Revises: 1e7978033bf2
Create Date: 2014-09-06 22:34:10.791372

"""

# revision identifiers, used by Alembic.
revision = '1aa2a2ddbd71'
down_revision = '1e7978033bf2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table('event_type',
        sa.Column('id', sa.Integer()),
        sa.Column('term_type', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        )

    event_type = table('event_type',
        column('term_type', sa.Integer()),
        column('event_id', sa.Integer()),
    )

    op.bulk_insert(event_type,
        [
            {'term_type': 0, 'event_id': 1},
            {'term_type': 0, 'event_id': 2},
            {'term_type': 0, 'event_id': 4},
            {'term_type': 1, 'event_id': 6},
        ]
    )

def downgrade_term():
    op.drop_table("event_type")


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


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


def downgrade_payment():
    pass


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
