"""edit person card column

Revision ID: 285541867a4b
Revises: 183116bf1b1c
Create Date: 2015-12-17 14:39:04.355684

"""

# revision identifiers, used by Alembic.
revision = '285541867a4b'
down_revision = '183116bf1b1c'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.alter_column('person', 'card',
                    existing_type=sa.String(12), nullable=True)


def downgrade_term():
    op.alter_column('person', 'card',
                    existing_type=sa.String(8), nullable=False)


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

