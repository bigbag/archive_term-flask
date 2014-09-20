"""add firm

Revision ID: 51b2b0684fc9
Revises: 1aa2a2ddbd71
Create Date: 2014-09-07 01:17:48.642315

"""

# revision identifiers, used by Alembic.
revision = '51b2b0684fc9'
down_revision = '1aa2a2ddbd71'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'hard_id',
        sa.Column('id', sa.Integer()),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('inn', sa.String(50), nullable=False),
        sa.Column('sub_domain', sa.Text(), nullable=False),
        sa.Column('pattern_id', sa.String(300), nullable=False, index=True),
        sa.Column('logo', sa.Text()),
        sa.Column('address', sa.Text()),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_unique_constraint("uq_firm_sub_domain", "firm", ["sub_domain"])


def downgrade_term():
    op.drop_table("firm")


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
