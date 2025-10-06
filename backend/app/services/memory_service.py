"""Memory service for FAISS vector storage and user memory management."""

import json
import hashlib
import base64
import os
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from loguru import logger

from app.core.config import settings


class MemoryService:
    """Memory service for FAISS vector storage and user memory management."""
    
    def __init__(self):
        """Initialize memory service."""
        self.embedding_model = None
        self.faiss_index = None
        self.index_path = settings.FAISS_INDEX_PATH
        self.embedding_model_name = settings.EMBEDDING_MODEL
        
        # Initialize embedding model and FAISS index
        self._init_embedding_model()
        self._init_faiss_index()
    
    def _init_embedding_model(self) -> None:
        """Initialize the sentence transformer model."""
        try:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info(f"✅ Embedding model loaded: {self.embedding_model_name}")
        except Exception as e:
            logger.error(f"❌ Error loading embedding model: {e}")
            self.embedding_model = None
    
    def _init_faiss_index(self) -> None:
        """Initialize or load FAISS index."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Try to load existing index
            if os.path.exists(self.index_path):
                self.faiss_index = faiss.read_index(self.index_path)
                logger.info(f"✅ FAISS index loaded from {self.index_path}")
            else:
                # Create new index
                dimension = self.embedding_model.get_sentence_embedding_dimension() if self.embedding_model else 384
                self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
                logger.info(f"✅ New FAISS index created with dimension {dimension}")
                
                # Save the index
                self._save_index()
                
        except Exception as e:
            logger.error(f"❌ Error initializing FAISS index: {e}")
            self.faiss_index = None
    
    def _save_index(self) -> None:
        """Save FAISS index to disk."""
        try:
            if self.faiss_index:
                faiss.write_index(self.faiss_index, self.index_path)
                logger.debug(f"FAISS index saved to {self.index_path}")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text."""
        if not self.embedding_model:
            return None
        
        try:
            embedding = self.embedding_model.encode([text])
            return embedding[0]
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None
    
    def _compute_content_hash(self, content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def store_memory(
        self,
        user_id: int,
        content: str,
        memory_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store a new memory with embedding."""
        try:
            if not self.embedding_model or not self.faiss_index:
                logger.warning("Embedding model or FAISS index not available")
                return False
            
            # Get embedding
            embedding = self._get_embedding(content)
            if embedding is None:
                return False
            
            # Compute content hash
            content_hash = self._compute_content_hash(content)
            
            # Prepare metadata
            memory_metadata = {
                "user_id": user_id,
                "content": content,
                "memory_type": memory_type,
                "content_hash": content_hash,
                "timestamp": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
            
            # Store in FAISS index
            embedding_reshaped = embedding.reshape(1, -1)
            vector_id = self.faiss_index.ntotal  # Get the next index ID
            self.faiss_index.add(embedding_reshaped)
            
            # Save index
            self._save_index()
            
            # Store vector_id in database
            try:
                from sqlalchemy.orm import Session
                from app.db.session import SessionLocal
                from ..models.memory import Memory
                
                # Create database session
                db = SessionLocal()
                
                try:
                    # Create new memory record with vector_id
                    memory = Memory(
                        user_id=user_id,
                        content=content,
                        memory_type=memory_type,
                        metadata=memory_metadata,
                        vector_id=int(vector_id)
                    )
                    db.add(memory)
                    db.commit()
                    logger.info(f"Memory stored with vector_id: {vector_id}")
                finally:
                    db.close()
            except Exception as db_err:
                logger.error(f"Error storing memory in database: {db_err}")
            
            logger.info(f"Memory stored for user {user_id}, type: {memory_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return False
    
    def search_memories(
        self,
        user_id: int,
        query: str,
        memory_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Keyword search across memories and related tables.

        This implementation queries the Memory table first and falls back to
        other domain tables (career, habits, finance) depending on the
        provided memory_type. DB sessions are created and closed safely.
        """
        try:
            from sqlalchemy.orm import Session
            from app.db.session import SessionLocal
            from ..models.memory import Memory
            from ..models.career import CareerGoal, UserSkill
            from ..models.habits import Habit
            from ..models.finance import Expense, FinancialGoal

            db = SessionLocal()
            results: List[Dict[str, Any]] = []

            try:
                # If memory_type specified, search targeted tables
                if memory_type:
                    if memory_type == "career":
                        career_goals = db.query(CareerGoal).filter(
                            CareerGoal.user_id == user_id,
                            (CareerGoal.title.ilike(f"%{query}%")) | (CareerGoal.description.ilike(f"%{query}%"))
                        ).limit(top_k).all()

                        for goal in career_goals:
                            results.append({
                                "score": 0.9,
                                "content": goal.title,
                                "description": goal.description,
                                "memory_type": "career",
                                "timestamp": goal.created_at.isoformat(),
                                "metadata": {
                                    "status": getattr(goal, "status", None),
                                    "priority": getattr(goal, "priority", None),
                                    "progress": getattr(goal, "progress", None)
                                }
                            })

                        # user skills
                        skills = db.query(UserSkill).filter(
                            UserSkill.user_id == user_id,
                            UserSkill.name.ilike(f"%{query}%")
                        ).limit(top_k).all()

                        for skill in skills:
                            results.append({
                                "score": 0.85,
                                "content": skill.name,
                                "description": f"Proficiency level: {getattr(skill, 'proficiency_level', None)}/10",
                                "memory_type": "career_skill",
                                "timestamp": skill.created_at.isoformat(),
                                "metadata": {
                                    "proficiency": getattr(skill, "proficiency_level", None),
                                    "years_experience": getattr(skill, "years_experience", None)
                                }
                            })

                    elif memory_type == "habits":
                        habits = db.query(Habit).filter(
                            Habit.user_id == user_id,
                            (Habit.name.ilike(f"%{query}%")) | (Habit.description.ilike(f"%{query}%"))
                        ).limit(top_k).all()

                        for habit in habits:
                            results.append({
                                "score": 0.9,
                                "content": habit.name,
                                "description": habit.description,
                                "memory_type": "habits",
                                "timestamp": habit.created_at.isoformat(),
                                "metadata": {
                                    "category": getattr(habit, "category", None),
                                    "frequency": getattr(habit, "frequency", None)
                                }
                            })

                    elif memory_type == "finance":
                        financial_goals = db.query(FinancialGoal).filter(
                            FinancialGoal.user_id == user_id,
                            (FinancialGoal.name.ilike(f"%{query}%")) | (FinancialGoal.description.ilike(f"%{query}%"))
                        ).limit(top_k).all()

                        for goal in financial_goals:
                            results.append({
                                "score": 0.9,
                                "content": goal.name,
                                "description": goal.description,
                                "memory_type": "finance",
                                "timestamp": goal.created_at.isoformat(),
                                "metadata": {
                                    "category": getattr(goal, "category", None),
                                    "target_amount": getattr(goal, "target_amount", None),
                                    "current_amount": getattr(goal, "current_amount", None)
                                }
                            })

                        expenses = db.query(Expense).filter(
                            Expense.user_id == user_id,
                            (Expense.description.ilike(f"%{query}%")) | (Expense.category.ilike(f"%{query}%"))
                        ).limit(top_k).all()

                        for expense in expenses:
                            results.append({
                                "score": 0.85,
                                "content": expense.description,
                                "description": f"{getattr(expense, 'amount', None)} spent on {getattr(expense, 'category', None)}",
                                "memory_type": "finance_expense",
                                "timestamp": expense.date.isoformat(),
                                "metadata": {
                                    "amount": getattr(expense, "amount", None),
                                    "category": getattr(expense, "category", None)
                                }
                            })

                else:
                    # Search Memory table first
                    memories = db.query(Memory).filter(
                        Memory.user_id == user_id,
                        Memory.content.ilike(f"%{query}%")
                    ).limit(top_k).all()

                    for memory in memories:
                        results.append({
                            "score": 0.95,
                            "content": memory.content,
                            "memory_type": memory.memory_type,
                            "timestamp": memory.created_at.isoformat(),
                            "metadata": memory.metadata
                        })

                    # If not enough, search career/habits/finance
                    if len(results) < top_k:
                        remaining = top_k - len(results)

                        career_goals = db.query(CareerGoal).filter(
                            CareerGoal.user_id == user_id,
                            (CareerGoal.title.ilike(f"%{query}%")) | (CareerGoal.description.ilike(f"%{query}%"))
                        ).limit(remaining).all()

                        for goal in career_goals:
                            results.append({
                                "score": 0.9,
                                "content": goal.title,
                                "description": goal.description,
                                "memory_type": "career",
                                "timestamp": goal.created_at.isoformat(),
                                "metadata": {
                                    "status": getattr(goal, "status", None),
                                    "priority": getattr(goal, "priority", None),
                                    "progress": getattr(goal, "progress", None)
                                }
                            })

                        remaining = top_k - len(results)

                        if remaining > 0:
                            habits = db.query(Habit).filter(
                                Habit.user_id == user_id,
                                (Habit.name.ilike(f"%{query}%")) | (Habit.description.ilike(f"%{query}%"))
                            ).limit(remaining).all()

                            for habit in habits:
                                results.append({
                                    "score": 0.85,
                                    "content": habit.name,
                                    "description": habit.description,
                                    "memory_type": "habits",
                                    "timestamp": habit.created_at.isoformat(),
                                    "metadata": {
                                        "category": getattr(habit, "category", None),
                                        "frequency": getattr(habit, "frequency", None)
                                    }
                                })

                            remaining = top_k - len(results)

                        if remaining > 0:
                            financial_goals = db.query(FinancialGoal).filter(
                                FinancialGoal.user_id == user_id,
                                (FinancialGoal.name.ilike(f"%{query}%")) | (FinancialGoal.description.ilike(f"%{query}%"))
                            ).limit(remaining).all()

                            for goal in financial_goals:
                                results.append({
                                    "score": 0.8,
                                    "content": goal.name,
                                    "description": goal.description,
                                    "memory_type": "finance",
                                    "timestamp": goal.created_at.isoformat(),
                                    "metadata": {
                                        "category": getattr(goal, "category", None),
                                        "target_amount": getattr(goal, "target_amount", None),
                                        "current_amount": getattr(goal, "current_amount", None)
                                    }
                                })

                # Sort and return top_k
                results.sort(key=lambda x: x.get("score", 0), reverse=True)
                return results[:top_k]

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
            
    def search_memories_with_rag(
        self,
        user_id: int,
        query: str,
        memory_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search memories using RAG (Retrieval Augmented Generation)."""
        # First try semantic search with FAISS
        results = self.semantic_search(user_id, query, memory_type, top_k)
        
        # If no results, fall back to keyword search
        if not results:
            results = self.search_memories(user_id, query, memory_type, top_k)
            
        return results
    
    def get_user_context(
        self,
        user_id: int,
        context_type: str = "general",
        max_memories: int = 10
    ) -> Dict[str, Any]:
        """Get user context for AI personalization."""
        try:
            from sqlalchemy.orm import Session
            from app.db.session import SessionLocal
            from ..models.career import CareerGoal
            from ..models.habits import Habit, HabitLog
            from ..models.finance import Budget, Expense, FinancialGoal
            from ..models.mood import MoodLog
            from ..models.user import User
            from ..models.career import Skill as UserSkill
            
            # Create database session
            db = SessionLocal()
            
            try:
                # Base context structure
                context = {
                    "user_id": user_id,
                    "context_type": context_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "recent_activities": [],
                    "preferences": {},
                    "goals": [],
                    "habits": [],
                    "mood_trends": [],
                    "financial_status": {},
                    "career_progress": {}
                }
                
                # Get user information
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    # Pull optional preferences from the JSON field to avoid attribute errors
                    try:
                        prefs = user.get_preferences() if hasattr(user, "get_preferences") else {}
                    except Exception:
                        prefs = {}

                    tz = (
                        (prefs.get("timezone") if isinstance(prefs, dict) else None)
                        or getattr(user, "timezone", None)
                        or "Asia/Kolkata"
                    )
                    theme = (
                        (prefs.get("theme") if isinstance(prefs, dict) else None)
                        or getattr(user, "theme_preference", None)
                        or "system"
                    )

                    context["preferences"] = {
                        "name": getattr(user, "name", None),
                        "email": getattr(user, "email", None),
                        "timezone": tz,
                        "theme": theme,
                        # Optionally include other onboarding preferences if present
                        "branch": (prefs.get("branch") if isinstance(prefs, dict) else None),
                        "year": (prefs.get("year") if isinstance(prefs, dict) else None),
                        "target_role": (prefs.get("target_role") if isinstance(prefs, dict) else None),
                        "interests": (prefs.get("interests") if isinstance(prefs, dict) else None),
                        "location": (prefs.get("location") if isinstance(prefs, dict) else None),
                    }
                
                # Add context based on type
                if context_type == "career" or context_type == "general":
                    # Get career goals
                    career_goals = db.query(CareerGoal).filter(
                        CareerGoal.user_id == user_id
                    ).order_by(CareerGoal.created_at.desc()).limit(max_memories).all()
                    
                    # Get user skills
                    user_skills = db.query(UserSkill).filter(
                        UserSkill.user_id == user_id
                    ).order_by(UserSkill.proficiency_level.desc()).limit(max_memories).all()
                    
                    # Format career progress data
                    context["career_progress"] = {
                        "current_goals": [goal.title for goal in career_goals if getattr(goal, "status", None) == "active"],
                        "skills_in_progress": [skill.name for skill in user_skills if (getattr(skill, "proficiency_score", 0) or 0) < 80],
                        "recent_achievements": [goal.title for goal in career_goals if getattr(goal, "status", None) == "completed"]
                    }
                
                if context_type == "habits" or context_type == "general":
                    # Get habits
                    habits = db.query(Habit).filter(
                        Habit.user_id == user_id
                    ).order_by(Habit.id.desc()).limit(max_memories).all()
                    
                    # Get recent habit logs
                    habit_logs = db.query(HabitLog).filter(
                        HabitLog.user_id == user_id
                    ).order_by(HabitLog.date.desc()).limit(max_memories).all()
                    
                    # Format habits data
                    context["habits"] = [habit.name for habit in habits]
                    
                    # Add streak information
                    habit_streaks = {}
                    for log in habit_logs:
                        if log.habit_id not in habit_streaks:
                            habit_streaks[log.habit_id] = 0
                        if log.completed:
                            habit_streaks[log.habit_id] += 1
                    
                    context["habit_streaks"] = habit_streaks
                
                if context_type == "finance" or context_type == "general":
                    # Get budget
                    budget = db.query(Budget).filter(
                        Budget.user_id == user_id
                    ).order_by(Budget.created_at.desc()).first()
                    
                    # Get financial goals
                    financial_goals = db.query(FinancialGoal).filter(
                        FinancialGoal.user_id == user_id
                    ).order_by(FinancialGoal.created_at.desc()).limit(max_memories).all()
                    
                    # Get recent expenses
                    expenses = db.query(Expense).filter(
                        Expense.user_id == user_id
                    ).order_by(Expense.date.desc()).limit(max_memories).all()
                    
                    # Format financial data
                    if budget:
                        context["financial_status"] = {
                            "monthly_budget": budget.total_amount,
                            "savings_goal": sum(goal.target_amount for goal in financial_goals if goal.category == "savings"),
                            "current_savings": sum(goal.current_amount for goal in financial_goals if goal.category == "savings"),
                            "recent_expenses": [{"amount": expense.amount, "category": expense.category} for expense in expenses]
                        }
                
                # Get mood trends
                mood_logs = db.query(MoodLog).filter(
                    MoodLog.user_id == user_id
                ).order_by(MoodLog.timestamp.desc()).limit(max_memories).all()
                
                if mood_logs:
                    context["mood_trends"] = [{"mood": log.mood_value, "date": log.timestamp.isoformat()} for log in mood_logs]
                
                return context
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return {"user_id": user_id, "error": "Failed to get context"}
            
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return {"user_id": user_id, "error": "Failed to get context"}
    
    def update_user_preferences(
        self,
        user_id: int,
        preferences: Dict[str, Any]
    ) -> bool:
        """Update user preferences in memory."""
        try:
            # Store preferences as a memory
            preferences_content = json.dumps(preferences, indent=2)
            success = self.store_memory(
                user_id=user_id,
                content=preferences_content,
                memory_type="preferences",
                metadata={"preferences": preferences}
            )
            
            if success:
                logger.info(f"User preferences updated for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False
    
    def get_personalized_suggestions(
        self,
        user_id: int,
        suggestion_type: str = "general"
    ) -> List[Dict[str, Any]]:
        """Get personalized suggestions based on user memory."""
        try:
            from sqlalchemy.orm import Session
            from app.db.session import SessionLocal
            from ..models.career import CareerGoal, UserSkill
            from ..models.habits import Habit, HabitLog
            from ..models.finance import Budget, Expense, FinancialGoal
            
            # Create database session
            db = SessionLocal()
            
            try:
                suggestions = []
                
                if suggestion_type == "habits" or suggestion_type == "general":
                    # Get user's habits
                    habits = db.query(Habit).filter(Habit.user_id == user_id).all()
                    habit_logs = db.query(HabitLog).filter(HabitLog.user_id == user_id).order_by(HabitLog.date.desc()).limit(10).all()
                    
                    # Generate suggestions based on habits
                    for habit in habits:
                        # Check completion rate
                        habit_logs_for_habit = [log for log in habit_logs if log.habit_id == habit.id]
                        completed_count = sum(1 for log in habit_logs_for_habit if log.completed)
                        total_count = len(habit_logs_for_habit)
                        
                        if total_count > 0 and completed_count / total_count < 0.5:
                            suggestions.append({
                                "type": "habit",
                                "title": f"Improve {habit.name}",
                                "description": f"Work on being more consistent with your {habit.name} habit",
                                "reason": "Your completion rate is below 50%",
                                "difficulty": "medium"
                            })
                
                if suggestion_type == "finance" or suggestion_type == "general":
                    # Get financial data
                    financial_goals = db.query(FinancialGoal).filter(FinancialGoal.user_id == user_id).all()
                    expenses = db.query(Expense).filter(Expense.user_id == user_id).order_by(Expense.date.desc()).limit(10).all()
                    
                    # Check if user has an emergency fund goal
                    has_emergency_fund = any(goal.category == "emergency_fund" for goal in financial_goals)
                    if not has_emergency_fund:
                        suggestions.append({
                            "type": "finance",
                            "title": "Emergency Fund",
                            "description": "Start building an emergency fund of 3-6 months of expenses",
                            "reason": "Financial security is important for peace of mind",
                            "priority": "high"
                        })
                    
                    # Check progress on financial goals
                    for goal in financial_goals:
                        if goal.target_amount > 0:
                            progress = goal.current_amount / goal.target_amount
                            if progress < 0.25:
                                suggestions.append({
                                    "type": "finance",
                                    "title": f"Boost {goal.name}",
                                    "description": f"Increase monthly contribution to your {goal.name} goal",
                                    "reason": "You're currently below 25% of your target",
                                    "priority": "medium"
                                })
                
                if suggestion_type == "career" or suggestion_type == "general":
                    # Get career data
                    career_goals = db.query(CareerGoal).filter(CareerGoal.user_id == user_id).all()
                    user_skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
                    
                    # Check if user has active career goals
                    active_goals = [goal for goal in career_goals if goal.status == "active"]
                    if not active_goals:
                        suggestions.append({
                            "type": "career",
                            "title": "Set Career Goal",
                            "description": "Define a specific career goal to work towards",
                            "reason": "Having clear goals improves focus and motivation",
                            "effort": "medium"
                        })
                    
                    # Suggest skill development based on career goals
                    for goal in active_goals:
                        # Check if user has skills related to their goals
                        user_skill_names = {skill.name.lower() for skill in user_skills}
                        if "programming" not in user_skill_names and "developer" in goal.title.lower():
                            suggestions.append({
                                "type": "career",
                                "title": "Learn Programming",
                                "description": "Start learning a programming language relevant to your career goal",
                                "reason": "Programming skills are essential for developer roles",
                                "effort": "high"
                            })
                
                return suggestions
                
            finally:
                db.close()
            
        except Exception as e:
            logger.error(f"Error getting personalized suggestions: {e}")
            return []

    def semantic_search(
        self,
        user_id: int,
        query: str,
        memory_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Semantic search using FAISS embeddings.

        Returns a list of matching memories enriched with score and metadata.
        Falls back to keyword search if embeddings or index are not available.
        """
        try:
            # If embedding model or FAISS index not ready, fallback
            if not self.embedding_model or not self.faiss_index:
                logger.warning("Embedding model or FAISS index not available, falling back to keyword search")
                return self.search_memories(user_id, query, memory_type, top_k)

            # Create embedding for the query
            query_embedding = self._get_embedding(query)
            if query_embedding is None:
                logger.warning("Failed to create embedding for query, falling back to keyword search")
                return self.search_memories(user_id, query, memory_type, top_k)

            # Reshape and search
            query_embedding = query_embedding.reshape(1, -1)
            distances, indices = self.faiss_index.search(query_embedding, top_k)

            from app.db.session import SessionLocal
            from ..models.memory import Memory

            db = SessionLocal()
            results: List[Dict[str, Any]] = []

            try:
                for i, idx in enumerate(indices[0]):
                    if idx < 0:
                        continue

                    # FAISS IndexFlatIP returns inner product similarity; treat distance as score
                    score = float(distances[0][i]) if distances is not None else 0.0

                    # Map FAISS index id to Memory.vector_id
                    memory = db.query(Memory).filter(
                        Memory.user_id == user_id,
                        Memory.vector_id == int(idx)
                    ).first()

                    if memory:
                        results.append({
                            "score": score,
                            "content": memory.content,
                            "memory_type": memory.memory_type,
                            "timestamp": memory.created_at.isoformat(),
                            "metadata": memory.metadata
                        })

                # If not enough semantic results, supplement with keyword search
                if len(results) < top_k:
                    keyword_results = self.search_memories(user_id, query, memory_type, top_k - len(results))
                    results.extend(keyword_results)

                # Sort and return
                results.sort(key=lambda x: x.get("score", 0), reverse=True)
                return results[:top_k]

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error in semantic_search: {e}")
            return self.search_memories(user_id, query, memory_type, top_k)
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if self.faiss_index:
                self._save_index()
            logger.info("Memory service cleanup completed")
        except Exception as e:
            logger.error(f"Error during memory service cleanup: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get memory service status."""
        return {
            "embedding_model_loaded": self.embedding_model is not None,
            "faiss_index_loaded": self.faiss_index is not None,
            "index_path": self.index_path,
            "embedding_model": self.embedding_model_name,
            "last_check": datetime.utcnow().isoformat()
        }
