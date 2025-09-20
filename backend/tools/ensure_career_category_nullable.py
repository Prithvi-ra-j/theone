"""
Small utility to ensure the careergoal.category column is nullable and has a default.
Run this from the activated venv: python backend\tools\ensure_career_category_nullable.py

It will connect using the DATABASE_URL from app.core.config (preferred) or from the
environment variable DATABASE_URL. It will run ALTER TABLE statements inside a
transaction and print the results. It will NOT drop or modify data.
"""
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text


def find_database_url():
    # Try to import app settings. Add parent (backend) to sys.path when running from tools/
    this_file = Path(__file__).resolve()
    backend_dir = this_file.parent.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    tried = []
    # 1) env var
    env_url = os.environ.get("DATABASE_URL")
    tried.append(f"env DATABASE_URL={env_url}")
    if env_url:
        return env_url, tried

    # 2) Try loading .env from backend root or repository root
    for candidate in [backend_dir / ".env", backend_dir.parent / ".env", backend_dir / "env.example"]:
        if candidate.exists():
            tried.append(f"found {candidate}")
            try:
                for line in candidate.read_text().splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("DATABASE_URL"):
                        # accept DATABASE_URL=... or export DATABASE_URL=...
                        kv = line.split("=", 1)
                        if len(kv) == 2:
                            val = kv[1].strip()
                            # strip surrounding quotes if present
                            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                                val = val[1:-1]
                            tried.append(f"{candidate}: parsed DATABASE_URL={val}")
                            return val, tried
            except Exception as e:
                tried.append(f"failed to parse {candidate}: {e}")

    # 3) Fallback to importing app core settings (may use different cwd for env file)
    try:
        from app.core.config import settings
        tried.append(f"app.core.config: settings.DATABASE_URL={getattr(settings, 'DATABASE_URL', None)}")
        if getattr(settings, "DATABASE_URL", None):
            return settings.DATABASE_URL, tried
    except Exception as e:
        tried.append(f"import app.core.config failed: {e}")

    return None, tried


DATABASE_URL, probes = find_database_url()
if DATABASE_URL is not None:
    # settings.DATABASE_URL may be a Pydantic PostgresDsn; convert to string
    try:
        DATABASE_URL = str(DATABASE_URL)
    except Exception:
        pass
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found. Tried:")
    for p in probes:
        print(" -", p)
    sys.exit(2)

print(f"Using DATABASE_URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)

alter_sql = '''
BEGIN;
ALTER TABLE IF EXISTS careergoal ALTER COLUMN category DROP NOT NULL;
ALTER TABLE IF EXISTS careergoal ALTER COLUMN category SET DEFAULT 'general';
COMMIT;
'''

try:
    with engine.connect() as conn:
        try:
            print("Applying ALTER TABLE to make careergoal.category nullable and set default...")
            conn.execute(text(alter_sql))
            print("Done. You may want to run alembic heads or inspect the schema to confirm.")
        except Exception as exc:
            print("Failed to apply changes:", exc)
            sys.exit(3)
except Exception as e:
    # Common failure: DB not reachable or auth failure
    msg = str(e)
    print("Failed to connect to the database:", msg)
    print("Possible causes:")
    print(" - DATABASE_URL credentials (username/password) are incorrect")
    print(" - PostgreSQL not running or not reachable on host/port")
    print(" - The running process can't reach localhost/127.0.0.1 due to networking or containerization")
    print("What you can do:")
    print(" - Check backend/.env and environment variable DATABASE_URL and ensure the password is correct.")
    print(" - If you changed .env, restart your shell/venv or export DATABASE_URL in the environment before rerunning.")
    print(" - Alternatively run alembic with the correct DATABASE_URL: cd backend && .\\venv311\\Scripts\\python.exe -m alembic upgrade head")
    sys.exit(4)
