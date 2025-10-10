"""split remaining conversation fields into a separate, SQLite-friendly migration

Revision ID: mn9o0p1q2r3
Revises: kl8m9n0o1p2
Create Date: 2025-10-10
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'mn9o0p1q2r3'
down_revision = 'kl8m9n0o1p2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    try:
        with op.batch_alter_table('conversation') as batch_op:
            batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')))
            batch_op.add_column(sa.Column('was_helpful', sa.Boolean(), nullable=True))
            batch_op.add_column(sa.Column('message_type', sa.String(length=50), nullable=False))
            batch_op.add_column(sa.Column('content', sa.Text(), nullable=False))
            batch_op.add_column(sa.Column('role', sa.String(length=20), nullable=False))
            batch_op.add_column(sa.Column('model_version', sa.String(length=50), nullable=True))
            batch_op.add_column(sa.Column('model_used', sa.String(length=100), nullable=True))
            batch_op.add_column(sa.Column('user_rating', sa.Integer(), nullable=True))
            batch_op.add_column(sa.Column('confidence', sa.Float(), nullable=True))
            batch_op.add_column(sa.Column('feedback_notes', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('processing_time', sa.Float(), nullable=True))
            batch_op.add_column(sa.Column('sentiment', sa.String(length=20), nullable=True))
            batch_op.add_column(sa.Column('message_index', sa.Integer(), nullable=False))
            batch_op.add_column(sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('now()')))
            batch_op.add_column(sa.Column('context', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('intent', sa.String(length=100), nullable=True))

            # drop legacy columns if present
            for col in ('ended_at','last_message_at','started_at','message_count','is_active','context_data','summary','messages','conversation_type'):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
    except Exception:
        # fallback to idempotent individual operations
        try:
            op.add_column('conversation', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')))
        except Exception:
            pass
        for col, col_def in [
            ('was_helpful', sa.Column('was_helpful', sa.Boolean(), nullable=True)),
            ('message_type', sa.Column('message_type', sa.String(length=50), nullable=False)),
            ('content', sa.Column('content', sa.Text(), nullable=False)),
            ('role', sa.Column('role', sa.String(length=20), nullable=False)),
            ('model_version', sa.Column('model_version', sa.String(length=50), nullable=True)),
            ('model_used', sa.Column('model_used', sa.String(length=100), nullable=True)),
            ('user_rating', sa.Column('user_rating', sa.Integer(), nullable=True)),
            ('confidence', sa.Column('confidence', sa.Float(), nullable=True)),
            ('feedback_notes', sa.Column('feedback_notes', sa.Text(), nullable=True)),
            ('processing_time', sa.Column('processing_time', sa.Float(), nullable=True)),
            ('sentiment', sa.Column('sentiment', sa.String(length=20), nullable=True)),
            ('message_index', sa.Column('message_index', sa.Integer(), nullable=False)),
            ('timestamp', sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('now()'))),
            ('context', sa.Column('context', sa.Text(), nullable=True)),
            ('intent', sa.Column('intent', sa.String(length=100), nullable=True)),
        ]:
            try:
                op.add_column('conversation', col_def)
            except Exception:
                pass
        for col in ('ended_at','last_message_at','started_at','message_count','is_active','context_data','summary','messages','conversation_type'):
            try:
                op.drop_column('conversation', col)
            except Exception:
                pass


def downgrade() -> None:
    try:
        with op.batch_alter_table('conversation') as batch_op:
            for col in ('created_at','was_helpful','message_type','content','role','model_version','model_used','user_rating','confidence','feedback_notes','processing_time','sentiment','message_index','timestamp','context','intent'):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
    except Exception:
        for col in ('created_at','was_helpful','message_type','content','role','model_version','model_used','user_rating','confidence','feedback_notes','processing_time','sentiment','message_index','timestamp','context','intent'):
            try:
                op.drop_column('conversation', col)
            except Exception:
                pass
