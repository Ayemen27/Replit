"""Add Bridge Tool tables

Revision ID: 20251116_192141
Revises: 
Create Date: 2025-11-16 19:21:41.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '20251116_192141'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('deployment_records',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tag', sa.String(length=100), nullable=False),
    sa.Column('author', sa.String(length=100), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('git_commit', sa.String(length=50), nullable=True),
    sa.Column('git_branch', sa.String(length=100), nullable=True),
    sa.Column('server_path', sa.String(length=500), nullable=True),
    sa.Column('files_count', sa.Integer(), nullable=True),
    sa.Column('errors', sa.Text(), nullable=True),
    sa.Column('duration_seconds', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deployment_records_tag'), 'deployment_records', ['tag'], unique=True)
    
    op.create_table('release_info',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tag', sa.String(length=100), nullable=False),
    sa.Column('deployment_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('deployed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('server_path', sa.String(length=500), nullable=True),
    sa.Column('git_commit', sa.String(length=50), nullable=True),
    sa.Column('rollback_count', sa.Integer(), nullable=True),
    sa.Column('last_rollback_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['deployment_id'], ['deployment_records.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_release_info_is_active'), 'release_info', ['is_active'], unique=False)
    op.create_index(op.f('ix_release_info_tag'), 'release_info', ['tag'], unique=True)
    
    op.create_table('file_changes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('deployment_id', sa.Integer(), nullable=False),
    sa.Column('file_path', sa.String(length=1000), nullable=False),
    sa.Column('change_type', sa.String(length=20), nullable=False),
    sa.Column('additions', sa.Integer(), nullable=True),
    sa.Column('deletions', sa.Integer(), nullable=True),
    sa.Column('staged', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['deployment_id'], ['deployment_records.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_file_changes_deployment_id'), 'file_changes', ['deployment_id'], unique=False)
    
    op.create_table('rollback_progress',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('rollback_id', sa.String(length=36), nullable=False),
    sa.Column('tag', sa.String(length=100), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('step', sa.String(length=50), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('percentage', sa.Integer(), nullable=True),
    sa.Column('previous_tag', sa.String(length=100), nullable=True),
    sa.Column('current_tag', sa.String(length=100), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rollback_progress_rollback_id'), 'rollback_progress', ['rollback_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_rollback_progress_rollback_id'), table_name='rollback_progress')
    op.drop_table('rollback_progress')
    op.drop_index(op.f('ix_file_changes_deployment_id'), table_name='file_changes')
    op.drop_table('file_changes')
    op.drop_index(op.f('ix_release_info_tag'), table_name='release_info')
    op.drop_index(op.f('ix_release_info_is_active'), table_name='release_info')
    op.drop_table('release_info')
    op.drop_index(op.f('ix_deployment_records_tag'), table_name='deployment_records')
    op.drop_table('deployment_records')
