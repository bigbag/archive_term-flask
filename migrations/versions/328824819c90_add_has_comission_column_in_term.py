"""add_has_comission_column_in_term
Revision ID: 328824819c90Revises: 3921918c588dCreate Date: 2015-09-04 13:48:58.611000
"""
# revision identifiers, used by Alembic.revision = '328824819c90'down_revision = '3921918c588d'
from alembic import opimport sqlalchemy as sa
def upgrade(engine_name):    eval("upgrade_%s" % engine_name)()

def downgrade(engine_name):    eval("downgrade_%s" % engine_name)()

def upgrade_term():    op.add_column('term', sa.Column(        'has_comission', sa.Integer(), nullable=True, server_default='1'))def downgrade_term():    op.drop_column('term', 'has_comission')
def upgrade_stack():    pass

def downgrade_stack():    pass
def upgrade_payment():    pass
def downgrade_payment():    pass
def upgrade_mobispot():    pass

def downgrade_mobispot():    pass