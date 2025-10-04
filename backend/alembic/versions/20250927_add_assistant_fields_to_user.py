"""add assistant fields to user

Revision ID: a27f2a9c1b01
Revises: d3f1a9b2c8e4
Create Date: 2025-09-27
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a27f2a9c1b01'
down_revision = 'd3f1a9b2c8e4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('assistant_avatar', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('assistant_personality', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('assistant_language', sa.String(length=50), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('assistant_language')
        batch_op.drop_column('assistant_personality')
        batch_op.drop_column('assistant_avatar')
