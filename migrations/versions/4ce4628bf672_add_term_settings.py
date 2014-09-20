"""add term_settings

Revision ID: 4ce4628bf672
Revises: 31625142e74a
Create Date: 2014-09-07 01:22:41.240934

"""

# revision identifiers, used by Alembic.
revision = '4ce4628bf672'
down_revision = '31625142e74a'

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    eval("upgrade_%s" % engine_name)()


def downgrade(engine_name):
    eval("downgrade_%s" % engine_name)()


def upgrade_term():
    op.create_table(
        'term_settings',
        sa.Column('id', sa.Integer()),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('download_status', sa.Integer(), nullable=False, index=True, server_default='1'),
        sa.Column('download_ip', sa.String(150), nullable=False, server_default=u'5.9.50.180'),
        sa.Column('download_port', sa.Integer(), nullable=False, server_default='4000'),
        sa.Column('download_proto', sa.String(150), nullable=False, server_default='https'),
        sa.Column('download_link_type', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('upload_status', sa.Integer(), nullable=False, index=True, server_default='1'),
        sa.Column('upload_ip', sa.String(150), nullable=False, server_default=u'5.9.50.180'),
        sa.Column('upload_port', sa.Integer(), nullable=False, server_default='4000'),
        sa.Column('upload_proto', sa.String(150), nullable=False, server_default='https'),
        sa.Column('upload_link_type', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('logger_status', sa.Integer(), nullable=False, index=True, server_default='1'),
        sa.Column('logger_ip', sa.String(150), nullable=False, server_default=u'5.9.50.180'),
        sa.Column('logger_port', sa.Integer(), nullable=False, server_default='9999'),
        sa.Column('logger_proto', sa.String(150), nullable=False, server_default='https'),
        sa.Column('logger_link_type', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('update_status', sa.Integer(), nullable=False, index=True, server_default='1'),
        sa.Column('update_ip', sa.String(150), nullable=False, server_default=u'5.9.50.180'),
        sa.Column('update_port', sa.Integer(), nullable=False, server_default='9999'),
        sa.Column('update_proto', sa.String(150), nullable=False, server_default='https'),
        sa.Column('update_link_type', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('keyload_status', sa.Integer(), nullable=False, index=True, server_default='1'),
        sa.Column('keyload_ip', sa.String(150), nullable=False, server_default=u'5.9.50.180'),
        sa.Column('keyload_port', sa.Integer(), nullable=False, server_default='9999'),
        sa.Column('keyload_proto', sa.String(150), nullable=False, server_default='https'),
        sa.Column('keyload_link_type', sa.Integer(), nullable=False, server_default='2'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade_term():
    op.drop_table("term_settings")


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
