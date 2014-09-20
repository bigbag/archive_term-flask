"""add term

Revision ID: 474560d8811d
Revises: 2258b5102d7b
Create Date: 2014-09-07 01:22:08.588577

"""

# revision identifiers, used by Alembic.
revision = '474560d8811d'
down_revision = '2258b5102d7b'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'term',
        sa.Column('id', sa.Integer()),
        sa.Column('hard_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('tz', sa.String(150), nullable=False, server_default=u'Europe/Moscow'),
        sa.Column('report_date', sa.DateTime()),
        sa.Column('config_date', sa.DateTime()),
        sa.Column('blacklist_date', sa.DateTime()),
        sa.Column('upload_start', sa.String(10), nullable=False, server_default='00:01'),
        sa.Column('upload_stop', sa.String(10), nullable=False, server_default='23:59'),
        sa.Column('upload_period', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('download_start', sa.String(10), nullable=False, server_default='00:01'),
        sa.Column('download_stop', sa.String(10), nullable=False, server_default='23:59'),
        sa.Column('download_period', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('blacklist', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('factor', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.Integer(), nullable=False, index=True, server_default='1'),
        sa.Column('settings_id', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('update_qid', sa.String(128), nullable=False, server_default='1'),
        sa.Column('keyload_qid', sa.String(128)),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_unique_constraint("uq_term_hard_id", "term", ["hard_id"])


def downgrade_term():
    op.drop_table("term")


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
