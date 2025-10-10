"""split achievement changes into a separate, SQLite-friendly migration

Revision ID: a1b2c3d4e5f6
Revises: make_career_category_nullable
Create Date: 2025-10-10 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'make_career_category_nullable'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    dialect = getattr(bind, 'dialect', None)
    dialect_name = getattr(dialect, 'name', '') if dialect is not None else ''

    # gather existing columns/constraints
    try:
        existing_cols = [c['name'] for c in inspector.get_columns('achievement')]
    except Exception:
        existing_cols = []
    try:
        existing_uniques = [u['name'] for u in inspector.get_unique_constraints('achievement') if u.get('name')]
    except Exception:
        existing_uniques = []
    try:
        existing_fks = [fk['name'] for fk in inspector.get_foreign_keys('achievement') if fk.get('name')]
    except Exception:
        existing_fks = []

    # Use batch_alter_table to perform collapse of adds/drops/alter in a single table recreation
    with op.batch_alter_table('achievement') as batch_op:
        # Add new columns if missing. For SQLite avoid server_default tokens that are Postgres-specific.
        def maybe_add(col_name, col_obj):
            if col_name not in existing_cols:
                if dialect_name == 'sqlite':
                    # create a copy without server_default for sqlite
                    new_col = sa.Column(col_obj.name, col_obj.type, nullable=col_obj.nullable)
                    batch_op.add_column(new_col)
                else:
                    batch_op.add_column(col_obj)

        maybe_add('name', sa.Column('name', sa.String(length=255), nullable=False, server_default=sa.text("''")))
        maybe_add('target_value', sa.Column('target_value', sa.Float(), nullable=False, server_default=sa.text('0')))
        maybe_add('measurement_unit', sa.Column('measurement_unit', sa.String(length=50), nullable=False, server_default=sa.text("''")))
        maybe_add('points_reward', sa.Column('points_reward', sa.Integer(), nullable=False, server_default=sa.text('0')))
        maybe_add('icon_url', sa.Column('icon_url', sa.String(length=500), nullable=True))
        maybe_add('difficulty_level', sa.Column('difficulty_level', sa.Integer(), nullable=False, server_default=sa.text('0')))
        maybe_add('is_active', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('false')))
        maybe_add('is_repeatable', sa.Column('is_repeatable', sa.Boolean(), nullable=False, server_default=sa.text('false')))
        maybe_add('updated_at', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')))

        # Alter description nullable -> False
        batch_op.alter_column('description', existing_type=sa.TEXT(), nullable=False)

        # create unique constraint on name if missing
        if 'uq_achievement_name' not in existing_uniques and 'name' in existing_cols:
            batch_op.create_unique_constraint('uq_achievement_name', ['name'])

        # drop FK if present
        if 'achievement_user_id_fkey' in existing_fks:
            batch_op.drop_constraint('achievement_user_id_fkey', type_='foreignkey')

        # drop deprecated columns if present
        for _col in ('value', 'user_id', 'title', 'rarity_score', 'difficulty', 'achieved_at', 'points_earned'):
            try:
                if _col in existing_cols:
                    batch_op.drop_column(_col)
            except Exception:
                pass


def downgrade() -> None:
    # Downgrade attempts to restore some dropped columns where possible.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    try:
        existing_cols = [c['name'] for c in inspector.get_columns('achievement')]
    except Exception:
        existing_cols = []

    with op.batch_alter_table('achievement') as batch_op:
        # restore removed columns only if missing (types are best-effort)
        for col_name, col_type in [
            ('value', sa.TEXT()),
            ('user_id', sa.INTEGER()),
            ('title', sa.VARCHAR(length=255)),
            ('rarity_score', sa.FLOAT()),
            ('difficulty', sa.VARCHAR(length=20)),
            ('achieved_at', sa.DateTime()),
            ('points_earned', sa.INTEGER()),
        ]:
            try:
                if col_name not in existing_cols:
                    batch_op.add_column(sa.Column(col_name, col_type, nullable=True))
            except Exception:
                pass
