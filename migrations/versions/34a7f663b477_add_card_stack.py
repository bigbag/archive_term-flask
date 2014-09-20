"""add card_stack

Revision ID: 34a7f663b477
Revises: 3282cc6eb403
Create Date: 2014-09-06 22:33:42.249145

"""

# revision identifiers, used by Alembic.
revision = '34a7f663b477'
down_revision = '3282cc6eb403'

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
        'card',
        sa.Column('id', sa.Integer()),
        sa.Column('term_id', sa.Integer(), nullable=False),
        sa.Column('payment_id', sa.String(20), nullable=False),
        sa.Column('creation_date', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_stack():
    op.drop_table("card")


def upgrade_payment():
    pass


def downgrade_payment():
    pass


def upgrade_mobispot():
    pass


def downgrade_mobispot():
    pass
