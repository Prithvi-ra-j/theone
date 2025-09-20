"""Simple verification helper to show counts for the demo user.

Run from backend root with the venv active:
  python tools\check_seed.py
"""
import sys
from pathlib import Path

this_file = Path(__file__).resolve()
backend_dir = this_file.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.models.user import User


DEMO_EMAIL = "demo.user@example.com"


def main():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == DEMO_EMAIL).first()
        if not user:
            print(f"No demo user found with email {DEMO_EMAIL}. Run the seeder first.")
            return

            print(f"Demo user found: id={user.id}, email={user.email}, name={user.name}")
            # Print counts using direct model queries to avoid join coercion issues
            from app.models.habits import Habit, Task, CalendarEvent
            from app.models.finance import Expense, Income, Budget, FinancialGoal
            from app.models.mood import MoodLog
            from app.models.career import CareerGoal

            print("Counts:")
            try:
                print(" - habits:", db.query(Habit).filter(Habit.user_id == user.id).count())
                print(" - tasks:", db.query(Task).filter(Task.user_id == user.id).count())
                print(" - events:", db.query(CalendarEvent).filter(CalendarEvent.user_id == user.id).count())
                print(" - expenses:", db.query(Expense).filter(Expense.user_id == user.id).count())
                print(" - incomes:", db.query(Income).filter(Income.user_id == user.id).count())
                print(" - budgets:", db.query(Budget).filter(Budget.user_id == user.id).count())
                print(" - financial goals:", db.query(FinancialGoal).filter(FinancialGoal.user_id == user.id).count())
                print(" - mood logs:", db.query(MoodLog).filter(MoodLog.user_id == user.id).count())
                print(" - career goals:", db.query(CareerGoal).filter(CareerGoal.user_id == user.id).count())
            except Exception as e:
                print("Failed to query counts:", e)

    finally:
        db.close()


if __name__ == "__main__":
    main()
