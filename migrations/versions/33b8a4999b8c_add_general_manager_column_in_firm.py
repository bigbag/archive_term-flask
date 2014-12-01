"""add general manager column in firm
Revision ID: 33b8a4999b8cRevises: 51698e9f4ac9Create Date: 2014-11-27 10:47:01.942000
"""
# revision identifiers, used by Alembic.
revision = '33b8a4999b8c'down_revision = '51698e9f4ac9'
from alembic import opimport sqlalchemy as sadef upgrade(engine_name):    eval("upgrade_%s" % engine_name)()def downgrade(engine_name):    eval("downgrade_%s" % engine_name)()def upgrade_term():    op.add_column('firm', sa.Column(        'general_manager', sa.String(128), nullable=True))def downgrade_term():    op.drop_column('firm', 'general_manager')def upgrade_stack():    passdef downgrade_stack():    passdef upgrade_payment():    pass    def downgrade_payment():    passdef upgrade_mobispot():    passdef downgrade_mobispot():    pass