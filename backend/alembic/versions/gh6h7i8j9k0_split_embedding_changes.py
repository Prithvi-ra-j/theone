"""split embedding changes into a separate, SQLite-friendly migration

Revision ID: gh6h7i8j9k0
Revises: ef5g6h7i8j9
Create Date: 2025-10-10
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'gh6h7i8j9k0'
down_revision = 'ef5g6h7i8j9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add embedding columns with dialect-aware types and drop deprecated ones
    try:
        bind = op.get_bind()
        dialect_name = getattr(getattr(bind,'dialect',None),'name','')
    except Exception:
        dialect_name = 'sqlite'

    if dialect_name == 'sqlite':
        vec_type = sa.BLOB()
        text_json_type = sa.Text()
    else:
        try:
            from sqlalchemy.dialects import postgresql
            vec_type = postgresql.BYTEA()
            text_json_type = postgresql.JSON()
        except Exception:
            vec_type = sa.LargeBinary()
            try:
                text_json_type = sa.JSON()
            except Exception:
                text_json_type = sa.Text()

    try:
        with op.batch_alter_table('embedding') as batch_op:
            batch_op.add_column(sa.Column('vector_dimension', sa.Integer(), nullable=False))
            batch_op.add_column(sa.Column('embedding_quality', sa.Float(), nullable=True))
            batch_op.add_column(sa.Column('embedding_version', sa.String(length=20), nullable=False))
            batch_op.add_column(sa.Column('embedding_model', sa.String(length=100), nullable=False))
            batch_op.add_column(sa.Column('embedding_vector', vec_type, nullable=False))
            batch_op.add_column(sa.Column('text_content', sa.Text(), nullable=False))

            # Drop unique constraint if present
            try:
                inspector = sa.inspect(bind)
                emb_uniques = [uc['name'] for uc in inspector.get_unique_constraints('embedding') if uc.get('name')]
            except Exception:
                emb_uniques = []

            if 'uq_embedding_memory_id' in emb_uniques:
                try:
                    batch_op.drop_constraint('uq_embedding_memory_id', type_='unique')
                except Exception:
                    pass

            for col in ('updated_at','is_valid','model_name','dimensions','vector'):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
    except Exception:
        # Fallback: try best-effort individual ops
        try:
            op.add_column('embedding', sa.Column('vector_dimension', sa.Integer(), nullable=False))
        except Exception:
            pass


def downgrade() -> None:
    try:
        with op.batch_alter_table('embedding') as batch_op:
            for col in ('vector_dimension','embedding_quality','embedding_version','embedding_model','embedding_vector','text_content'):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
    except Exception:
        for col in ('vector_dimension','embedding_quality','embedding_version','embedding_model','embedding_vector','text_content'):
            try:
                op.drop_column('embedding', col)
            except Exception:
                pass
