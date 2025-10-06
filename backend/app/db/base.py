# Import all the models, so that Base has them before being imported by Alembic
from .session import Base  # noqa

# Import all models here for Alembic to detect them
# This ensures all models are registered with the Base metadata
from ..models.user import User  # noqa
from ..models.career import CareerGoal, Skill, LearningPath  # noqa
from ..models.habits import Habit, HabitCompletion, Task, CalendarEvent  # noqa
from ..models.finance import Expense, Budget, Income, FinancialGoal  # noqa
from ..models.mood import MoodLog  # noqa
from ..models.gamification import Badge, UserBadge, Achievement, UserAchievement, UserStats  # noqa
from ..models.memory import UserMemory, Embedding, Conversation  # noqa
from ..models.mini_assistant import MiniAssistant, AssistantInteraction  # noqa
from ..models.journal import JournalEntry, JournalAnalysis  # noqa