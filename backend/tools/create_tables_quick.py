"""Developer helper: create all tables using SQLAlchemy metadata.create_all().

Not recommended for production; this is a quick convenience to get local dev DB
ready so seed scripts and frontend can be tested without running alembic.
"""
import sys
from pathlib import Path

this_file = Path(__file__).resolve()
backend_dir = this_file.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.session import engine
from app.db.session import Base

# Import all model modules so SQLAlchemy metadata is fully populated
# (create_all uses Base.metadata; importing ensures model classes register)
try:
    import app.models.user
    import app.models.habits
    import app.models.finance
    import app.models.mood
    import app.models.career
    import app.models.gamification
    import app.models.memory
except Exception:
    # If any import fails, continue and create tables for what's available
    pass


def main():
    print("Creating database tables via SQLAlchemy metadata.create_all()")
    Base.metadata.create_all(bind=engine)
    print("Done.")


if __name__ == "__main__":
    main()
