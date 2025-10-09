"""make careergoal.category nullable

Revision ID: make_career_category_nullable
Revises: 04aa8b881b32
Create Date: 2025-09-20 20:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'make_career_category_nullable'
down_revision = '04aa8b881b32'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite doesn't support ALTER COLUMN directly; use batch_alter_table
    with op.batch_alter_table('careergoal') as batch_op:
        batch_op.alter_column('category', existing_type=sa.String(length=100), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('careergoal') as batch_op:
        batch_op.alter_column('category', existing_type=sa.String(length=100), nullable=False)
