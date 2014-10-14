"""add_blacklist_settings

Revision ID: 31c8c264892c
Revises: 53c2fbd73b89
Create Date: 2014-10-14 13:35:59.638916

"""

# revision identifiers, used by Alembic.
revision = '31c8c264892c'
down_revision = '53c2fbd73b89'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'blacklist_settings',
        sa.Column('term_id', sa.Integer()),
        sa.Column('partial_on_restart', sa.Integer(), server_default='1'),
        sa.Column('partial_timeout', sa.Integer(), server_default='5'),
        sa.Column('full_on_restart', sa.Integer(), server_default='1'),
        sa.Column('full_timeout', sa.Integer(), server_default='5'),
    )
    op.create_primary_key("pk_blacklist_settings_term_id", "blacklist_settings", ["term_id"])


def downgrade_term():
    op.drop_table("blacklist_settings")


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
