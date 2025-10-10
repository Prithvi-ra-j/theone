"""split calendarevent changes into a separate, SQLite-friendly migration

Revision ID: ij7k8l9m0n1
Revises: gh6h7i8j9k0
Create Date: 2025-10-10
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ij7k8l9m0n1'
down_revision = 'gh6h7i8j9k0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    try:
        with op.batch_alter_table('calendarevent') as batch_op:
            batch_op.add_column(sa.Column('start_time', sa.Time(), nullable=True))
            # If there are other calendarevent changes, add them here in batch
    except Exception:
        try:
            op.add_column('calendarevent', sa.Column('start_time', sa.Time(), nullable=True))
        except Exception:
            pass


def downgrade() -> None:
    try:
        with op.batch_alter_table('calendarevent') as batch_op:
            try:
                batch_op.drop_column('start_time')
            except Exception:
                pass
    except Exception:
        try:
            op.drop_column('calendarevent', 'start_time')
        except Exception:
            pass
