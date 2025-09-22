"""add usermemory vector_id

Revision ID: 20250922_add_usermemory_vector_id
Revises: 
Create Date: 2025-09-22 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250922_add_usermemory_vector_id'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add a nullable vector_id column to usermemory. If FAISS ids must be unique in future,
    # add a unique constraint in a subsequent migration after data backfill.
    with op.batch_alter_table('usermemory') as batch_op:
        batch_op.add_column(sa.Column('vector_id', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('usermemory') as batch_op:
        batch_op.drop_column('vector_id')
