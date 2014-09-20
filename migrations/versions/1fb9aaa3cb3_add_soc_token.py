"""add soc_token

Revision ID: 1fb9aaa3cb3
Revises: 27c2a878d5e1
Create Date: 2014-09-07 01:21:00.793520

"""

# revision identifiers, used by Alembic.
revision = '1fb9aaa3cb3'
down_revision = '27c2a878d5e1'

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
        'soc_token',
        sa.Column('id', sa.Integer()),
        sa.Column('type', sa.Integer(), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('soc_id', sa.String(512), nullable=False),
        sa.Column('soc_email', sa.Text()),
        sa.Column('user_token', sa.Text()),
        sa.Column('token_secret', sa.Text()),
        sa.Column('token_expires', sa.Integer()),
        sa.Column('is_tech', sa.Integer()),
        sa.Column('allow_login', sa.Integer()),
        sa.Column('soc_username', sa.Text()),
        sa.Column('refresh_token', sa.Text()),
        sa.Column('write_access', sa.Text()),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_mobispot():
    op.drop_table("soc_token")
