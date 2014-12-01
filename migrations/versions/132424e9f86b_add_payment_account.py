"""add payment_account
Revision ID: 132424e9f86bRevises: 90846d67fadCreate Date: 2014-11-20 16:59:14.127000
"""# revision identifiers, used by Alembic.revision = '132424e9f86b'down_revision = '90846d67fad'
from alembic import opimport sqlalchemy as sa
def upgrade(engine_name):    eval("upgrade_%s" % engine_name)()    
def downgrade(engine_name):    eval("downgrade_%s" % engine_name)()

def upgrade_term():    pass
def downgrade_term():    pass
def upgrade_stack():    pass    
def downgrade_stack():    pass
def upgrade_payment():    op.create_table(        'account',        sa.Column('id', sa.Integer()),        sa.Column('firm_id', sa.Integer(), nullable=False, index=True),        sa.Column('generated_date', sa.DateTime(), nullable=False, index=True),        sa.Column('summ', sa.Integer(), nullable=False),        sa.Column('items_count', sa.Integer(), nullable=True),        sa.Column('status', sa.Integer(), nullable=False, index=True, server_default='0'),    )    op.create_primary_key("pk_account_id", "account", ["id"])
def downgrade_payment():    op.drop_table('account')
def upgrade_mobispot():    pass
def downgrade_mobispot():    pass