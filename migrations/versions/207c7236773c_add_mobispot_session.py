"""add_mobispot_session

Revision ID: 207c7236773c
Revises: 56418a4c705
Create Date: 2014-09-21 00:36:17.292785

"""

# revision identifiers, used by Alembic.
revision = '207c7236773c'
down_revision = '56418a4c705'

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
        'session',
        sa.Column('id', sa.String(32)),
        sa.Column('expire', sa.Integer()),
        sa.Column('data', sa.Binary()),
    )

    op.create_primary_key("pk_session_id", "session", ["id"])


def downgrade_mobispot():
    passop.drop_table("session")
