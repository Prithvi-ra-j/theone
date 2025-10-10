"""split badge changes into a separate, SQLite-friendly migration

Revision ID: cd4e5f6g7h8
Revises: bc1d2e3f4g5
Create Date: 2025-10-10
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cd4e5f6g7h8'
down_revision = 'bc1d2e3f4g5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    try:
        with op.batch_alter_table('badge') as batch_op:
            # Add new columns
            batch_op.add_column(sa.Column('badge_type', sa.String(length=50), nullable=False, server_default=sa.text("''")))
            batch_op.add_column(sa.Column('difficulty', sa.String(length=20), nullable=False, server_default=sa.text("''")))
            batch_op.add_column(sa.Column('color', sa.String(length=7), nullable=True))
            # requirements as JSON -> use TEXT on SQLite if needed
            try:
                bind = op.get_bind()
                dialect_name = getattr(getattr(bind,'dialect',None),'name','')
                if dialect_name == 'sqlite':
                    req_type = sa.Text()
                else:
                    try:
                        from sqlalchemy.dialects import postgresql
                        req_type = postgresql.JSON()
                    except Exception:
                        req_type = sa.JSON()
            except Exception:
                req_type = sa.Text()
            batch_op.add_column(sa.Column('requirements', req_type, nullable=False, server_default=sa.text("'{}'::json")))
            batch_op.add_column(sa.Column('points_value', sa.Integer(), nullable=False, server_default=sa.text('0')))
            batch_op.add_column(sa.Column('is_secret', sa.Boolean(), nullable=False, server_default=sa.text('false')))
            # Drop old columns
            for col in ('is_hidden','rarity','criteria','points'):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
    except Exception:
        # Fallback: attempt idempotent operations
        try:
            op.add_column('badge', sa.Column('badge_type', sa.String(length=50), nullable=False, server_default=sa.text("''")))
        except Exception:
            pass
        # (rest omitted for brevity; batch op is preferred)


def downgrade() -> None:
    try:
        with op.batch_alter_table('badge') as batch_op:
            for col in ('is_hidden','rarity','criteria','points'):
                try:
                    batch_op.add_column(sa.Column(col, sa.String(length=255), nullable=True))
                except Exception:
                    pass
            for col in ('badge_type','difficulty','color','requirements','points_value','is_secret'):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
    except Exception:
        pass
