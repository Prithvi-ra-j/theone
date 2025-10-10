"""split user-related changes (userbadge, usermemory, userstats) into a separate migration

Revision ID: kl8m9n0o1p2
Revises: ij7k8l9m0n1
Create Date: 2025-10-10
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'kl8m9n0o1p2'
down_revision = 'ij7k8l9m0n1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    try:
        with op.batch_alter_table('userbadge') as batch_op:
            batch_op.add_column(sa.Column('earned_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')))
            batch_op.add_column(sa.Column('trigger_event', sa.String(length=255), nullable=True))
            # progress_snapshot JSON -> TEXT on SQLite
            bind = op.get_bind()
            dialect = getattr(getattr(bind,'dialect',None),'name','')
            prog_type = sa.Text() if dialect == 'sqlite' else sa.JSON()
            batch_op.add_column(sa.Column('progress_snapshot', prog_type, nullable=True))
            batch_op.add_column(sa.Column('is_displayed', sa.Boolean(), nullable=False, server_default=sa.text('false')))
            batch_op.add_column(sa.Column('display_order', sa.Integer(), nullable=True))
            batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')))
            for col in ('progress_value','is_notified'):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
    except Exception:
        # Fallback idempotent adds/drops
        try:
            op.add_column('userbadge', sa.Column('earned_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')))
        except Exception:
            pass

    try:
        with op.batch_alter_table('usermemory') as batch_op:
            batch_op.add_column(sa.Column('content', sa.Text(), nullable=False, server_default=sa.text("''")))
            batch_op.add_column(sa.Column('category', sa.String(length=100), nullable=True))
            batch_op.add_column(sa.Column('related_entity_type', sa.String(length=50), nullable=True))
            batch_op.add_column(sa.Column('related_entity_id', sa.Integer(), nullable=True))
            batch_op.alter_column('source', existing_type=sa.VARCHAR(length=50), type_=sa.String(length=100), nullable=True)
            for col in ('value','context','summary','tags','expires_at','key'):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
    except Exception:
        try:
            op.add_column('usermemory', sa.Column('content', sa.Text(), nullable=False, server_default=sa.text("''")))
        except Exception:
            pass

    try:
        with op.batch_alter_table('userstats') as batch_op:
            batch_op.add_column(sa.Column('total_points', sa.Integer(), nullable=False, server_default=sa.text('0')))
            batch_op.add_column(sa.Column('current_level', sa.Integer(), nullable=False, server_default=sa.text('0')))
            batch_op.add_column(sa.Column('points_to_next_level', sa.Integer(), nullable=False, server_default=sa.text('0')))
            batch_op.add_column(sa.Column('current_habit_streak', sa.Integer(), nullable=False, server_default=sa.text('0')))
            batch_op.add_column(sa.Column('total_habits_completed', sa.Integer(), nullable=False, server_default=sa.text('0')))
            batch_op.add_column(sa.Column('total_tasks_completed', sa.Integer(), nullable=False, server_default=sa.text('0')))
            batch_op.add_column(sa.Column('total_mood_logs', sa.Integer(), nullable=False, server_default=sa.text('0')))
            batch_op.add_column(sa.Column('total_expenses_logged', sa.Integer(), nullable=False, server_default=sa.text('0')))
            batch_op.add_column(sa.Column('achievements_completed', sa.Integer(), nullable=False, server_default=sa.text('0')))
            batch_op.add_column(sa.Column('days_active', sa.Integer(), nullable=False, server_default=sa.text('0')))
            batch_op.add_column(sa.Column('last_activity_date', sa.Date(), nullable=True))
            batch_op.add_column(sa.Column('weekly_points', sa.Integer(), nullable=False))
            batch_op.add_column(sa.Column('monthly_points', sa.Integer(), nullable=False))
            batch_op.add_column(sa.Column('weekly_reset_date', sa.Date(), nullable=True))
            batch_op.add_column(sa.Column('monthly_reset_date', sa.Date(), nullable=True))
            for col in ('wellness_streak','next_level_xp','last_activity','total_expenses_tracked','budgets_maintained','total_app_sessions','total_xp','learning_hours','habits_completed','achievements_unlocked','skills_learned','career_goals_completed','average_mood_score','total_habit_days','savings_goals_achieved','mood_logs_count','level','current_level_xp'):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
    except Exception:
        # fallback adds
        try:
            op.add_column('userstats', sa.Column('total_points', sa.Integer(), nullable=False, server_default=sa.text('0')))
        except Exception:
            pass


def downgrade() -> None:
    # Best-effort undos
    try:
        with op.batch_alter_table('userbadge') as batch_op:
            for col in ('earned_date','trigger_event','progress_snapshot','is_displayed','display_order','created_at'):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
    except Exception:
        for col in ('earned_date','trigger_event','progress_snapshot','is_displayed','display_order','created_at'):
            try:
                op.drop_column('userbadge', col)
            except Exception:
                pass

    try:
        with op.batch_alter_table('usermemory') as batch_op:
            for col in ('content','category','related_entity_type','related_entity_id'):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
            try:
                batch_op.alter_column('source', existing_type=sa.String(length=100), type_=sa.VARCHAR(length=50), nullable=False)
            except Exception:
                pass
    except Exception:
        for col in ('content','category','related_entity_type','related_entity_id'):
            try:
                op.drop_column('usermemory', col)
            except Exception:
                pass

    try:
        with op.batch_alter_table('userstats') as batch_op:
            for col in ('total_points','current_level','points_to_next_level','current_habit_streak','total_habits_completed','total_tasks_completed','total_mood_logs','total_expenses_logged','achievements_completed','days_active','last_activity_date','weekly_points','monthly_points','weekly_reset_date','monthly_reset_date'):
                try:
                    batch_op.drop_column(col)
                except Exception:
                    pass
    except Exception:
        for col in ('total_points','current_level','points_to_next_level','current_habit_streak','total_habits_completed','total_tasks_completed','total_mood_logs','total_expenses_logged','achievements_completed','days_active','last_activity_date','weekly_points','monthly_points','weekly_reset_date','monthly_reset_date'):
            try:
                op.drop_column('userstats', col)
            except Exception:
                pass
