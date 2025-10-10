"""split moodlog changes into a separate, SQLite-friendly migration

Revision ID: bc1d2e3f4g5
Revises: a1b2c3d4e5f6
Create Date: 2025-10-10
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'bc1d2e3f4g5'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use batch_alter_table to change JSON columns to TEXT and drop deprecated columns
    try:
        with op.batch_alter_table('moodlog') as batch_op:
            batch_op.alter_column('activities',
                   existing_type=sa.JSON(),
                   type_=sa.Text(),
                   existing_nullable=True)
            batch_op.alter_column('triggers',
                   existing_type=sa.JSON(),
                   type_=sa.Text(),
                   existing_nullable=True)

            batch_op.alter_column('entry_method',
                   existing_type=sa.VARCHAR(length=20),
                   server_default=None,
                   existing_nullable=False)
            batch_op.alter_column('is_private',
                   existing_type=sa.BOOLEAN(),
                   server_default=None,
                   existing_nullable=False)

            for col in ('motivation_level','confidence_level','mood_label',
                        'productivity_rating','water_intake','goals_completed'):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
    except Exception:
        # fallback: individual idempotent operations
        try:
            op.alter_column('moodlog', 'entry_method',
                       existing_type=sa.VARCHAR(length=20),
                       server_default=None,
                       existing_nullable=False)
        except Exception:
            pass
        for col in ('motivation_level','confidence_level','mood_label',
                    'productivity_rating','water_intake','goals_completed'):
            try:
                op.drop_column('moodlog', col)
            except Exception:
                pass


def downgrade() -> None:
    # Best-effort restore: add back dropped columns as nullable/with defaults where possible
    try:
        with op.batch_alter_table('moodlog') as batch_op:
            for col in ('motivation_level','confidence_level','mood_label',
                        'productivity_rating','water_intake','goals_completed'):
                try:
                    # Types are approximate; adjust if you need exact types back
                    if col in ('motivation_level','confidence_level','productivity_rating','goals_completed'):
                        batch_op.add_column(sa.Column(col, sa.Integer(), nullable=True))
                    elif col == 'water_intake':
                        batch_op.add_column(sa.Column(col, sa.Float(), nullable=True))
                    else:
                        batch_op.add_column(sa.Column(col, sa.String(length=50), nullable=True))
                except Exception:
                    pass
            # convert TEXT back to JSON where possible (no-op on SQLite)
            try:
                batch_op.alter_column('activities', existing_type=sa.Text(), type_=sa.JSON(), existing_nullable=True)
            except Exception:
                pass
            try:
                batch_op.alter_column('triggers', existing_type=sa.Text(), type_=sa.JSON(), existing_nullable=True)
            except Exception:
                pass
    except Exception:
        # best-effort fallbacks
        for col in ('motivation_level','confidence_level','mood_label',
                    'productivity_rating','water_intake','goals_completed'):
            try:
                op.add_column('moodlog', sa.Column(col, sa.Integer(), nullable=True))
            except Exception:
                pass
        try:
            op.alter_column('moodlog', 'activities', existing_type=sa.Text(), type_=sa.JSON(), existing_nullable=True)
        except Exception:
            pass
        try:
            op.alter_column('moodlog', 'triggers', existing_type=sa.Text(), type_=sa.JSON(), existing_nullable=True)
        except Exception:
            pass
