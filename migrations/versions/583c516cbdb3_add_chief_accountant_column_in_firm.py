"""add chief accountant column in firm
Revision ID: 583c516cbdb3Revises: 33b8a4999b8cCreate Date: 2014-11-27 10:49:12.105000
"""
# revision identifiers, used by Alembic.
revision = '583c516cbdb3'down_revision = '33b8a4999b8c'
from alembic import opimport sqlalchemy as sadef upgrade(engine_name):    eval("upgrade_%s" % engine_name)()def downgrade(engine_name):    eval("downgrade_%s" % engine_name)()def upgrade_term():    op.add_column('firm', sa.Column(        'chief_accountant', sa.String(128), nullable=True))def downgrade_term():    op.drop_column('firm', 'chief_accountant')def upgrade_stack():    passdef downgrade_stack():    passdef upgrade_payment():    pass    def downgrade_payment():    passdef upgrade_mobispot():    passdef downgrade_mobispot():    pass