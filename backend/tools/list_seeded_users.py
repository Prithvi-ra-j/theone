"""List seeded users and per-user data counts.

Run from backend root with the venv active:
  python tools\list_seeded_users.py
"""
from pathlib import Path
import sys
this_file = Path(__file__).resolve()
backend_dir = this_file.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal, engine
from app.models.user import User
from sqlalchemy import inspect

KEY_MODELS = {
    'habits': ('app.models.habits', 'Habit', 'user_id'),
    'tasks': ('app.models.habits', 'Task', 'user_id'),
    'events': ('app.models.habits', 'CalendarEvent', 'user_id'),
    'expenses': ('app.models.finance', 'Expense', 'user_id'),
    'incomes': ('app.models.finance', 'Income', 'user_id'),
    'budgets': ('app.models.finance', 'Budget', 'user_id'),
    'financial_goals': ('app.models.finance', 'FinancialGoal', 'user_id'),
    'career_goals': ('app.models.career', 'CareerGoal', 'user_id'),
}

def safe_import(module_path, name):
    try:
        module = __import__(module_path, fromlist=[name])
        return getattr(module, name)
    except Exception:
        return None

def main():
    db = SessionLocal()
    inspector = inspect(engine)
    has_mood_table = 'moodlog' in inspector.get_table_names()
    MoodLog = safe_import('app.models.mood', 'MoodLog') if has_mood_table else None

    users = db.query(User).all()
    if not users:
        print('No users found in DB.')
        return

    print('Found users:')
    for u in users:
        print(f'\n- id={u.id}  email={u.email}  name={u.name}')
        # default seeded password (if created by seeder): demopass123
        print('  - suggested login password (if seeded by demo scripts): demopass123')
        # Counts
        for label, (modpath, clsname, user_field) in KEY_MODELS.items():
            Model = safe_import(modpath, clsname)
            if Model is None:
                print(f'    - {label}: (model not available)')
                continue
            try:
                c = db.query(Model).filter(getattr(Model, user_field) == u.id).count()
                print(f'    - {label}: {c}')
            except Exception as e:
                print(f'    - {label}: query failed ({e})')
        # mood logs
        if MoodLog is not None:
            try:
                c = db.query(MoodLog).filter(MoodLog.user_id == u.id).count()
                print(f'    - mood_logs: {c}')
            except Exception as e:
                print(f'    - mood_logs: query failed ({e})')
        else:
            print('    - mood_logs: (mood table not present or missing columns)')

    db.close()

if __name__ == '__main__':
    main()
