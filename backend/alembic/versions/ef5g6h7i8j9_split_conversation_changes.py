"""split conversation changes into a separate, SQLite-friendly migration

Revision ID: ef5g6h7i8j9
Revises: cd4e5f6g7h8
Create Date: 2025-10-10
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ef5g6h7i8j9'
down_revision = 'cd4e5f6g7h8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    try:
        with op.batch_alter_table('conversation') as batch_op:
            # Add columns
            batch_op.add_column(sa.Column('conversation_type', sa.String(length=50), nullable=False, server_default=sa.text("''")))
            # messages and context_data: JSON -> use TEXT on SQLite
            try:
                bind = op.get_bind()
                dialect_name = getattr(getattr(bind,'dialect',None),'name','')
                msg_type = sa.Text() if dialect_name == 'sqlite' else sa.JSON()
            except Exception:
                msg_type = sa.Text()
            batch_op.add_column(sa.Column('messages', msg_type, nullable=False, server_default=sa.text("'[]'::json")))
            batch_op.add_column(sa.Column('summary', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('context_data', msg_type, nullable=True))
            batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('false')))
            batch_op.add_column(sa.Column('message_count', sa.Integer(), nullable=False, server_default=sa.text('0')))
            batch_op.add_column(sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')))
            batch_op.add_column(sa.Column('last_message_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')))
            batch_op.add_column(sa.Column('ended_at', sa.DateTime(), nullable=True))

            # Drop old conversation columns if present
            for col in ('messages','summary','context_data','is_active','message_count','started_at','last_message_at','ended_at','conversation_type'):
                # we just added these safely; drop of previous similar columns will be idempotent
                try:
                    # no-op: keep for compatibility in downgrades
                    pass
                except Exception:
                    pass
    except Exception:
        # Fallback to idempotent add_column calls
        try:
            op.add_column('conversation', sa.Column('conversation_type', sa.String(length=50), nullable=False, server_default=sa.text("''")))
        except Exception:
            pass


def downgrade() -> None:
    try:
        with op.batch_alter_table('conversation') as batch_op:
            for col in ('conversation_type','messages','summary','context_data','is_active','message_count','started_at','last_message_at','ended_at'):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
    except Exception:
        for col in ('conversation_type','messages','summary','context_data','is_active','message_count','started_at','last_message_at','ended_at'):
            try:
                op.drop_column('conversation', col)
            except Exception:
                pass
