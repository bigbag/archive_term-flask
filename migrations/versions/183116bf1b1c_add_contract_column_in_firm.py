"""add contract column in firm
Revision ID: 183116bf1b1cRevises: 3d4fab9bee8aCreate Date: 2015-12-02 11:39:04.811000
"""
# revision identifiers, used by Alembic.revision = '183116bf1b1c'down_revision = '3d4fab9bee8a'
from alembic import opimport sqlalchemy as sa
def upgrade(engine_name):    eval("upgrade_%s" % engine_name)()
def downgrade(engine_name):    eval("downgrade_%s" % engine_name)()
def upgrade_term():    op.add_column('firm', sa.Column(        'contract', sa.String(256), nullable=True))def downgrade_term():    op.drop_column('firm', 'contract')
def upgrade_stack():    pass

def downgrade_stack():    pass
def upgrade_payment():    pass

def downgrade_payment():    pass

def upgrade_mobispot():    pass
def downgrade_mobispot():    pass