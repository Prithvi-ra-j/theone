"""merge learningpath and journal heads

Revision ID: 4e359f91e3e9
Revises: 20250927_add_learningpath_items, 20251002_add_journal_tables
Create Date: 2025-10-02 19:44:13.492511

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e359f91e3e9'
down_revision = ('20250927_add_learningpath_items', '20251002_add_journal_tables')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass