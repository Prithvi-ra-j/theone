# Import all the models, so that Base has them before being imported by Alembic
from app.db.session import Base  # noqa

# Import all models here for Alembic to detect them
# This ensures all models are registered with the Base metadata
from app.models.user import User  # noqa
from app.models.career import CareerGoal, Skill, LearningPath  # noqa
from app.models.habits import Habit, HabitCompletion, Task, CalendarEvent  # noqa
from app.models.finance import Expense, Budget, Income, FinancialGoal  # noqa
from app.models.mood import MoodLog  # noqa
from app.models.gamification import Badge, UserBadge, Achievement, UserAchievement, UserStats  # noqa
from app.models.memory import UserMemory, Embedding, Conversation  # noqa
from app.models.mini_assistant import MiniAssistant, AssistantInteraction  # noqa
from app.models.journal import JournalEntry, JournalAnalysis  # noqa