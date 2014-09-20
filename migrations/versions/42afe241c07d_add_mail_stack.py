"""add mail_stack

Revision ID: 42afe241c07d
Revises: 3324739f958a
Create Date: 2014-09-07 01:18:25.788161

"""

# revision identifiers, used by Alembic.
revision = '42afe241c07d'
down_revision = '3324739f958a'

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
    op.create_table(
        'mail',
        sa.Column('id', sa.Integer()),
        sa.Column('senders', sa.Text(), nullable=False),
        sa.Column('recipients', sa.Text(), nullable=False),
        sa.Column('subject', sa.Text(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('attach', sa.Text()),
        sa.Column('creation_date', sa.DateTime(), nullable=False),
        sa.Column('lock', sa.Integer(), nullable=False, index=True, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_stack():
    op.drop_table("mail")


def upgrade_payment():
    pass


def downgrade_payment():
    pass


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
