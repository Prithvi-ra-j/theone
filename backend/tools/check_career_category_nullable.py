import sys
import os
import traceback

try:
    # Ensure repo root (backend) is on sys.path so `app` package can be imported
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from app.core.config import settings
    import psycopg2

    print('Using DATABASE_URL:', str(settings.DATABASE_URL))
    conn = psycopg2.connect(str(settings.DATABASE_URL))
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT is_nullable, column_default, data_type FROM information_schema.columns WHERE table_name='careergoal' AND column_name='category'"
        )
        row = cur.fetchone()
        print('careergoal.category ->', row)
        cur.execute("SELECT version_num FROM alembic_version")
        print('alembic_version ->', cur.fetchone())
    finally:
        # Best-effort cleanup of DB resources
        try:
            if cur is not None:
                cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
except Exception:
    print('Error checking DB:')
    traceback.print_exc()
    raise