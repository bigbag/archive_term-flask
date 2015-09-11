"""add_has_gprs_column_in_term
Revision ID: 3921918c588dRevises: 5904c7707b91Create Date: 2015-09-04 10:22:47.014000
"""
# revision identifiers, used by Alembic.revision = '3921918c588d'down_revision = '5904c7707b91'
from alembic import opimport sqlalchemy as sa
def upgrade(engine_name):    eval("upgrade_%s" % engine_name)()
def downgrade(engine_name):    eval("downgrade_%s" % engine_name)()
def upgrade_term():    op.add_column('term', sa.Column(        'has_gprs', sa.Integer(), nullable=True, server_default='1'))

def downgrade_term():    op.drop_column('term', 'has_gprs')
def upgrade_stack():    pass
def downgrade_stack():    pass
def upgrade_payment():    pass
def downgrade_payment():    pass
def upgrade_mobispot():    pass
def downgrade_mobispot():    pass