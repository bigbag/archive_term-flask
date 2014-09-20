"""add person_event

Revision ID: 33d1d88987a7
Revises: 189e9f074071
Create Date: 2014-09-07 01:20:16.261205

"""

# revision identifiers, used by Alembic.
revision = '33d1d88987a7'
down_revision = '189e9f074071'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'person_event',
        sa.Column('id', sa.Integer()),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('term_id', sa.Integer(), nullable=False, index=True),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('firm_id', sa.Integer(), nullable=False, index=True),
        sa.Column('timeout', sa.Integer(), server_default='5'),
        sa.Column('status', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_term():
    op.drop_table("person_event")


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
