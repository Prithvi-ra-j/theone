"""add learning path milestones and projects tables

Revision ID: 20250927_add_learningpath_items
Revises: 
Create Date: 2025-09-27
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250927_add_learningpath_items'
# Set this migration to follow the latest merge head so we don't create a new head
# The latest merged head in this repo is 'a27f2a9c1b01' (add assistant fields to user)
down_revision = 'a27f2a9c1b01'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'learningpath_milestone',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('learning_path_id', sa.Integer(), sa.ForeignKey('learningpath.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=True),
        sa.Column('estimated_weeks', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='planned'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'learningpath_project',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('learning_path_id', sa.Integer(), sa.ForeignKey('learningpath.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=True),
        sa.Column('est_hours', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='planned'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade():
    op.drop_table('learningpath_project')
    op.drop_table('learningpath_milestone')
