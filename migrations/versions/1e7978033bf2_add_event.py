"""add event

Revision ID: 1e7978033bf2
Revises: 34a7f663b477
Create Date: 2014-09-06 22:33:55.358293

"""

# revision identifiers, used by Alembic.
revision = '1e7978033bf2'
down_revision = '34a7f663b477'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'event',
        sa.Column('id', sa.Integer()),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('key', sa.String(150), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_term():
    op.drop_table("event")


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
