"""Raw-counts per user using direct SQL to avoid ORM column selection errors.
Run: python tools\get_seeded_user_counts.py
"""
from pathlib import Path
import sys
this_file = Path(__file__).resolve()
backend_dir = this_file.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.session import engine
from sqlalchemy import text, inspect

TABLES = [
    'habit', 'task', 'calendarevent', 'expense', 'income', 'budget', 'financialgoal', 'careergoal', 'moodlog'
]

with engine.connect() as conn:
    # get users
    users_res = conn.execute(text('SELECT id, email, name FROM "user" ORDER BY id'))
    users = users_res.fetchall()
    if not users:
        print('No users found.')
        sys.exit(0)

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    for u in users:
        uid = u[0]
        email = u[1]
        name = u[2]
        print(f'User id={uid} email={email} name={name}')
        print('  suggested password (if seeded by demo): demopass123')
        for t in TABLES:
            if t not in existing_tables:
                print(f'   - {t}: (table missing)')
                continue
            try:
                res = conn.execute(text(f'SELECT COUNT(*) FROM {t} WHERE user_id = :uid'), {'uid': uid})
                cnt = res.scalar()
                print(f'   - {t}: {cnt}')
            except Exception as e:
                print(f'   - {t}: query error ({e.__class__.__name__}: {e})')
        print('')
