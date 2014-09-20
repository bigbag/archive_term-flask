"""add user

Revision ID: 1d387a956397
Revises: 37cc2c8fec34
Create Date: 2014-09-07 01:23:06.190543

"""

# revision identifiers, used by Alembic.
revision = '1d387a956397'
down_revision = '37cc2c8fec34'

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
        'user',
        sa.Column('id', sa.Integer()),
        sa.Column('email', sa.String(128), nullable=False),
        sa.Column('password', sa.String(128), nullable=False),
        sa.Column('activkey', sa.String(128), nullable=False),
        sa.Column('creation_date', sa.DateTime(), nullable=False),
        sa.Column('lastvisit', sa.DateTime()),
        sa.Column('type', sa.Integer(), nullable=False, index=True, server_default='0'),
        sa.Column('status', sa.Integer(), nullable=False, index=True, server_default='0'),
        sa.Column('lang', sa.String(128), nullable=False, index=True, server_default='en'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_unique_constraint("uq_user_email", "user", ["email"])


def downgrade_mobispot():
    op.drop_table("user")
