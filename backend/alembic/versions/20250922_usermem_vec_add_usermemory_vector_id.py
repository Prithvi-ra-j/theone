"""add usermemory vector_id

Revision ID: 20250922_usermem_vec
Revises: 
Create Date: 2025-09-22 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250922_usermem_vec'
down_revision = None
branch_labels = None
depends_on = None


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    """Return True if column_name exists on table_name."""
    inspector = sa.inspect(conn)
    cols = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in cols


def upgrade():
    conn = op.get_bind()
    if not _column_exists(conn, 'usermemory', 'vector_id'):
        # Add the nullable vector_id column to usermemory
        with op.batch_alter_table('usermemory') as batch_op:
            batch_op.add_column(sa.Column('vector_id', sa.String(length=255), nullable=True))


def downgrade():
    conn = op.get_bind()
    if _column_exists(conn, 'usermemory', 'vector_id'):
        with op.batch_alter_table('usermemory') as batch_op:
            batch_op.drop_column('vector_id')
