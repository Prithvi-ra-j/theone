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
    # Make the careergoal.category column nullable
    op.alter_column('careergoal', 'category', existing_type=sa.String(length=100), nullable=True)


def downgrade() -> None:
    # Revert to not nullable (be careful: existing NULLs will cause failure)
    op.alter_column('careergoal', 'category', existing_type=sa.String(length=100), nullable=False)
