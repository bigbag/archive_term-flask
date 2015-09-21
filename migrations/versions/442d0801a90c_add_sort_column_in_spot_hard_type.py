"""add_sort_column_in_spot_hard_type
Revision ID: 442d0801a90cRevises: 164d9cafe331Create Date: 2015-09-21 12:29:53.178000
"""
# revision identifiers, used by Alembic.revision = '442d0801a90c'down_revision = '164d9cafe331'
from alembic import opimport sqlalchemy as sa
def upgrade(engine_name):    eval("upgrade_%s" % engine_name)()

def downgrade(engine_name):    eval("downgrade_%s" % engine_name)()

def upgrade_term():    pass

def downgrade_term():    pass

def upgrade_stack():    pass
def downgrade_stack():    pass

def upgrade_payment():    pass

def downgrade_payment():    pass
def upgrade_mobispot():    op.add_column('spot_hard_type', sa.Column(        'sort', sa.Integer(), nullable=True))    op.create_index('ik_spot_hard_type_sort', 'spot_hard_type', ['sort'])def downgrade_mobispot():    op.drop_index('ik_spot_hard_type_sort', 'spot_hard_type')    op.drop_column('spot_hard_type', 'sort')    