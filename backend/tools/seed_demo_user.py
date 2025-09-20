"""Seed script to create a demo user with ~1 week of data across modules.

Run inside the activated backend venv:
  python backend\tools\seed_demo_user.py

The script is idempotent: if the demo user email exists it will exit to avoid duplicates.
"""
from datetime import datetime, date, timedelta, time
from decimal import Decimal
import random
import sys
from pathlib import Path

# Ensure the backend package root is on sys.path so imports like `app.xxx` work
# whether the script is run from repository root, backend, or backend/tools.
this_file = Path(__file__).resolve()
backend_dir = this_file.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.db.session import engine
from app.models.user import User
from app.models.habits import Habit, Task, CalendarEvent, HabitCompletion
from app.models.finance import Expense, Budget, Income, FinancialGoal
# Don't import MoodLog at module import time because the running DB schema may differ from the ORM
# and importing the model can cause SQLAlchemy to issue queries that reference missing columns.
# We'll import MoodLog inside seed_mood_and_career after checking the DB schema.
from app.models.career import CareerGoal
from app.utils.security import hash_password


import argparse

DEMO_EMAIL = "demo.user@example.com"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--email", default=DEMO_EMAIL, help="Demo user email")
    p.add_argument("--force", action="store_true", help="Delete existing demo user and recreate")
    return p.parse_args()


def create_demo_user(db, email=DEMO_EMAIL, force=False):
    existing = db.query(User).filter(User.email == email).first()
    if existing and not force:
        print(f"Demo user already exists (email={email}), aborting seed to avoid duplicates.")
        return existing

    if existing and force:
        print(f"Reusing existing demo user {email} by updating fields as --force was provided")
        # Update existing user fields in-place to avoid FK delete issues
        existing.hashed_password = hash_password("demopass123")
        existing.name = "Demo User"
        existing.bio = "This is a seeded demo user for UI/UX previews."
        existing.avatar_url = None
        existing.phone_number = "+10000000000"
        existing.is_active = True
        existing.is_verified = True
        existing.is_superuser = False
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    user = User(
        email=email,
        hashed_password=hash_password("demopass123"),
        name="Demo User",
        bio="This is a seeded demo user for UI/UX previews.",
        avatar_url=None,
        phone_number="+10000000000",
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created demo user id={user.id}")
    return user


def seed_habits(db, user):
    habits = [
        {"name": "Morning Run", "category": "health", "frequency": "daily", "target_value": 30, "unit": "minutes"},
        {"name": "Read", "category": "learning", "frequency": "daily", "target_value": 20, "unit": "pages"},
    ]
    created = []
    for h in habits:
        db_h = Habit(
            user_id=user.id,
            name=h["name"],
            description=f"Demo habit: {h['name']}",
            category=h["category"],
            frequency=h["frequency"],
            target_value=h["target_value"],
            unit=h["unit"],
            preferred_time=time(7, 0),
            reminder_enabled=True,
            reminder_time=time(6, 45),
        )
        db.add(db_h)
        db.commit()
        db.refresh(db_h)
        created.append(db_h)

        # Add a week's completions for each habit
        today = date.today()
        for i in range(7):
            d = today - timedelta(days=6 - i)
            comp = HabitCompletion(
                user_id=user.id,
                habit_id=db_h.id,
                completed_date=d,
                actual_value=(db_h.target_value or 0) * (0.9 + 0.2 * random.random()),
                quality_rating=random.randint(3, 5),
                notes=f"Auto-seeded completion for {d}",
            )
            db.add(comp)
        db.commit()

    return created


def seed_tasks_events(db, user):
    tasks = [
        {"title": "Finish project plan", "due_days": 2, "priority": "high"},
        {"title": "Grocery shopping", "due_days": 1, "priority": "medium"},
        {"title": "Call mentor", "due_days": 3, "priority": "low"},
    ]
    created_tasks = []
    for t in tasks:
        due = date.today() + timedelta(days=t["due_days"])
        db_t = Task(
            user_id=user.id,
            title=t["title"],
            description=f"Demo task: {t['title']}",
            priority=t["priority"],
            due_date=due,
            reminder_enabled=False,
            category="personal",
        )
        db.add(db_t)
        db.commit()
        db.refresh(db_t)
        created_tasks.append(db_t)

    # Add a couple of calendar events across the coming week
    events = []
    start = datetime.combine(date.today() + timedelta(days=1), time(10, 0))
    for i in range(4):
        s = start + timedelta(days=i)
        e = s + timedelta(hours=1)
        ev = CalendarEvent(
            user_id=user.id,
            title=f"Demo Event {i+1}",
            description="Demo calendar event",
            start_datetime=s,
            end_datetime=e,
            all_day=False,
            location="Remote",
            is_virtual=True,
            meeting_link="https://example.com/meet",
        )
        db.add(ev)
        db.commit()
        db.refresh(ev)
        events.append(ev)

    return created_tasks, events


def seed_finance(db, user):
    # Expenses over last 7 days
    expenses = []
    categories = ["food", "transport", "entertainment", "groceries"]
    for i in range(7):
        d = date.today() - timedelta(days=i)
        exp = Expense(
            user_id=user.id,
            amount=Decimal(str(round(5 + random.random() * 45, 2))),
            description=f"Demo expense {i+1}",
            category=random.choice(categories),
            date=d,
            payment_method="card",
        )
        db.add(exp)
        expenses.append(exp)
    db.commit()

    # Budget
    budget = Budget(
        user_id=user.id,
        name="Monthly Groceries",
        category="groceries",
        amount=Decimal("300.00"),
        period_type="monthly",
        start_date=date.today().replace(day=1),
        end_date=None,
        spent_amount=Decimal("75.00"),
    )
    db.add(budget)

    # Income
    income = Income(
        user_id=user.id,
        amount=Decimal("1500.00"),
        source="salary",
        date_received=date.today() - timedelta(days=3),
        is_recurring=True,
        recurring_frequency="monthly",
    )
    db.add(income)

    # Financial goal
    fg = FinancialGoal(
        user_id=user.id,
        title="Emergency Fund",
        description="Save 3 months of expenses",
        goal_type="savings",
        target_amount=Decimal("5000.00"),
        current_amount=Decimal("450.00"),
        target_date=date.today() + timedelta(days=180),
    )
    db.add(fg)

    db.commit()
    return expenses, budget, income, fg


def seed_mood_and_career(db, user):
    moods = []
    today = date.today()
    # Inspect actual DB columns so we only set fields that exist in the running schema
    from sqlalchemy import inspect
    inspector = inspect(engine)
    db_table_names = inspector.get_table_names()
    mood_columns = {c['name'] for c in inspector.get_columns('moodlog')} if 'moodlog' in db_table_names else set()

    # Compare ORM model columns vs DB columns; if DB is missing any model columns, skip mood seeding
    # Import models now that we can check the DB schema
    from app.models.mood import MoodLog
    from app.models.career import CareerGoal

    model_cols = {c.name for c in MoodLog.__table__.columns}
    missing = model_cols - mood_columns
    if missing:
        print("Skipping mood seeding because the DB schema is missing MoodLog columns:", missing)
        print("You can run tools/create_tables_quick.py or apply migrations to add these columns.")
        # Still attempt to create a simple career goal below, so return empty moods
        moods = []
        # Create career goal later
        cg = CareerGoal(
            user_id=user.id,
            title="Complete Certification",
            description="Finish the cloud certification course and pass exam",
            category="certification",
            target_date=datetime.utcnow() + timedelta(days=60),
            priority="high",
            progress_percentage=15.0,
        )
        db.add(cg)
        db.commit()
        db.refresh(cg)
        return moods, cg

    from datetime import datetime, time as dtime
    for i in range(7):
        d = today - timedelta(days=i)
        # Build kwargs defensively to avoid inserting into non-existent columns
        mood_kwargs = {
            'user_id': user.id,
            'mood_score': random.randint(5, 9),
            'energy_level': random.randint(4, 9),
            'stress_level': random.randint(1, 5),
            'activities': ["reading", "run"] if random.random() > 0.5 else ["work"],
            'sleep_hours': round(6 + random.random() * 2, 1),
            'sleep_quality': random.randint(6, 9),
            'exercise_minutes': random.randint(20, 45),
            'notes': f"Demo mood log for {d}",
            'log_date': d,
        }

        # Optionally set primary_emotion if the column exists in DB schema
        if 'primary_emotion' in mood_columns:
            mood_kwargs['primary_emotion'] = random.choice(["happy", "content", "motivated"])

        # Optionally set secondary_emotions if present
        if 'secondary_emotions' in mood_columns:
            mood_kwargs['secondary_emotions'] = None

        # Set logged_at if required by DB schema
        if 'logged_at' in mood_columns:
            # Use log_date at noon for demo, or utcnow if not available
            mood_kwargs['logged_at'] = datetime.combine(d, dtime(12, 0))

        m = MoodLog(**{k: v for k, v in mood_kwargs.items() if k in mood_columns or k in ('user_id', 'mood_score')})
        db.add(m)
        moods.append(m)
    db.commit()

    # Career goals
    cg = CareerGoal(
        user_id=user.id,
        title="Complete Certification",
        description="Finish the cloud certification course and pass exam",
        category="certification",
        target_date=datetime.utcnow() + timedelta(days=60),
        priority="high",
        progress_percentage=15.0,
    )
    db.add(cg)
    db.commit()
    db.refresh(cg)

    return moods, cg


def main():
    args = parse_args()
    db = SessionLocal()
    try:
        user = create_demo_user(db, email=args.email, force=args.force)
        if not user:
            return

        h = seed_habits(db, user)
        tasks, events = seed_tasks_events(db, user)
        expenses, budget, income, fg = seed_finance(db, user)
        moods, cg = seed_mood_and_career(db, user)

        print("\nSeeding complete:")
        print(f" Habits created: {len(h)}")
        print(f" Tasks created: {len(tasks)}")
        print(f" Events created: {len(events)}")
        print(f" Expenses created: {len(expenses)}")
        print(f" Budget: {budget.name if budget else 'None'}")
        print(f" Income: {income.amount if income else 'None'}")
        print(f" Financial goal: {fg.title if fg else 'None'}")
        print(f" Mood logs: {len(moods)}")
        print(f" Career goal: {cg.title if cg else 'None'}")

    except Exception as e:
        print("Seeding failed:", e)
    finally:
        db.close()


if __name__ == "__main__":
    main()
