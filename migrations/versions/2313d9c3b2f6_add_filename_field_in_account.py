"""add_filename_field_in_account

Revision ID: 2313d9c3b2f6
Revises: 583c516cbdb3
Create Date: 2014-12-02 11:57:24.979872

"""

# revision identifiers, used by Alembic.
revision = '2313d9c3b2f6'
down_revision = '583c516cbdb3'

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
    op.add_column('account', sa.Column(
        'filename', sa.String(128), nullable=True))


def downgrade_payment():
    op.drop_column('account', 'filename')


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
