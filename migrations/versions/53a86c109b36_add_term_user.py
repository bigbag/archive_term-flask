"""add term_user

Revision ID: 53a86c109b36
Revises: 4ce4628bf672
Create Date: 2014-09-07 01:22:45.565279

"""

# revision identifiers, used by Alembic.
revision = '53a86c109b36'
down_revision = '4ce4628bf672'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'term_user',
        sa.Column('id', sa.Integer()),
        sa.Column('email', sa.String(128), nullable=False),
        sa.Column('password', sa.String(128), nullable=False),
        sa.Column('activkey', sa.String(128), nullable=False),
        sa.Column('creation_date', sa.DateTime),
        sa.Column('lastvisit', sa.DateTime),
        sa.Column('group', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('api_key', sa.String(150)),
        sa.Column('api_secret', sa.String(150)),
        sa.Column('status', sa.Integer(), nullable=False, index=True, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_unique_constraint("uq_term_user_email", "term_user", ["email"])


def downgrade_term():
    op.drop_table("term_user")


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
