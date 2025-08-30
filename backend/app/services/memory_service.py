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
            self.faiss_index.add(embedding_reshaped)
            
            # Save index
            self._save_index()
            
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
        """Search memories using semantic similarity."""
        try:
            if not self.embedding_model or not self.faiss_index:
                logger.warning("Embedding model or FAISS index not available")
                return []
            
            # Get query embedding
            query_embedding = self._get_embedding(query)
            if query_embedding is None:
                return []
            
            # Search in FAISS index
            query_reshaped = query_embedding.reshape(1, -1)
            scores, indices = self.faiss_index.search(query_reshaped, top_k)
            
            # For MVP, return placeholder results
            # In production, you'd store metadata separately and retrieve based on indices
            results = []
            for i, score in enumerate(scores[0]):
                if score > 0.5:  # Similarity threshold
                    results.append({
                        "score": float(score),
                        "content": f"Memory {i+1}",
                        "memory_type": "general",
                        "timestamp": datetime.utcnow().isoformat(),
                        "metadata": {"similarity_score": float(score)}
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    def get_user_context(
        self,
        user_id: int,
        context_type: str = "general",
        max_memories: int = 10
    ) -> Dict[str, Any]:
        """Get user context for AI personalization."""
        try:
            # For MVP, return placeholder context
            # In production, this would aggregate user data from various sources
            
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
            
            # Add some sample data for demonstration
            if context_type == "career":
                context["career_progress"] = {
                    "current_goals": ["Learn Python", "Build portfolio"],
                    "skills_in_progress": ["Data Science", "Web Development"],
                    "recent_achievements": ["Completed Python basics"]
                }
            elif context_type == "habits":
                context["habits"] = [
                    "Daily exercise",
                    "Reading",
                    "Meditation"
                ]
            elif context_type == "finance":
                context["financial_status"] = {
                    "monthly_budget": 5000,
                    "savings_goal": 10000,
                    "current_savings": 3000
                }
            
            return context
            
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
            # Get user context
            context = self.get_user_context(user_id, suggestion_type)
            
            # For MVP, return placeholder suggestions
            # In production, this would use AI to generate personalized suggestions
            
            suggestions = []
            
            if suggestion_type == "habits":
                suggestions = [
                    {
                        "type": "habit",
                        "title": "Morning Routine",
                        "description": "Start your day with 10 minutes of meditation",
                        "reason": "Based on your wellness goals",
                        "difficulty": "easy"
                    },
                    {
                        "type": "habit",
                        "title": "Skill Practice",
                        "description": "Dedicate 30 minutes daily to skill development",
                        "reason": "Aligns with your career goals",
                        "difficulty": "medium"
                    }
                ]
            elif suggestion_type == "finance":
                suggestions = [
                    {
                        "type": "finance",
                        "title": "Emergency Fund",
                        "description": "Start building an emergency fund of ₹10,000",
                        "reason": "Based on your current savings",
                        "priority": "high"
                    }
                ]
            elif suggestion_type == "career":
                suggestions = [
                    {
                        "type": "career",
                        "title": "Project Portfolio",
                        "description": "Build a small project to showcase your Python skills",
                        "reason": "Will help with your career goals",
                        "effort": "medium"
                    }
                ]
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting personalized suggestions: {e}")
            return []
    
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
