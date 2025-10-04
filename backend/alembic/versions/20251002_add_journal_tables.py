"""add journal tables

Revision ID: 20251002_add_journal_tables
Revises: a27f2a9c1b01
Create Date: 2025-10-02
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251002_add_journal_tables'
down_revision = 'a27f2a9c1b01'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'journal_entry',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False, index=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('user_mood', sa.Integer(), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_journal_entry_id', 'journal_entry', ['id'])
    op.create_index('ix_journal_entry_user_id', 'journal_entry', ['user_id'])

    op.create_table(
        'journal_analysis',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('journal_id', sa.Integer(), sa.ForeignKey('journal_entry.id'), nullable=False, index=True),
        sa.Column('mood_score', sa.Float(), nullable=True),
        sa.Column('valence', sa.Float(), nullable=True),
        sa.Column('arousal', sa.Float(), nullable=True),
        sa.Column('emotions', sa.JSON(), nullable=True),
        sa.Column('topics', sa.JSON(), nullable=True),
        sa.Column('triggers', sa.JSON(), nullable=True),
        sa.Column('suggestions', sa.JSON(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('safety_flags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_journal_analysis_id', 'journal_analysis', ['id'])
    op.create_index('ix_journal_analysis_journal_id', 'journal_analysis', ['journal_id'])


def downgrade() -> None:
    op.drop_index('ix_journal_analysis_journal_id', table_name='journal_analysis')
    op.drop_index('ix_journal_analysis_id', table_name='journal_analysis')
    op.drop_table('journal_analysis')

    op.drop_index('ix_journal_entry_user_id', table_name='journal_entry')
    op.drop_index('ix_journal_entry_id', table_name='journal_entry')
    op.drop_table('journal_entry')
