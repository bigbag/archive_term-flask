"""add_term_session

Revision ID: 56418a4c705
Revises: 43c11bf27fed
Create Date: 2014-09-21 00:36:10.484518

"""

# revision identifiers, used by Alembic.
revision = '56418a4c705'
down_revision = '43c11bf27fed'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'session',
        sa.Column('id', sa.String(32)),
        sa.Column('expire', sa.Integer()),
        sa.Column('data', sa.Binary()),
    )

    op.create_primary_key("pk_session_id", "session", ["id"])


def downgrade_term():
    op.drop_table("session")


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
