"""AI service for Ollama integration with LangChain."""

import json
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, SystemMessage
from loguru import logger

from app.core.config import settings


class AIService:
    """AI service for Ollama integration."""
    
    def __init__(self):
        """Initialize AI service."""
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.model_name = settings.OLLAMA_MODEL
        self.llm = None
        self.is_available = False
        
        # Initialize Ollama connection
        self._init_ollama()
    
    def _init_ollama(self) -> None:
        """Initialize Ollama connection."""
        try:
            # Test Ollama connection
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.ollama_base_url}/api/tags")
                if response.status_code == 200:
                    self.is_available = True
                    self.llm = Ollama(
                        base_url=self.ollama_base_url,
                        model=self.model_name,
                        temperature=0.7
                    )
                    logger.info(f"✅ Ollama connected successfully with model: {self.model_name}")
                else:
                    logger.warning(f"⚠️ Ollama connection failed: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Ollama connection error: {e}")
            self.is_available = False
    
    async def career_advisor(
        self,
        user_context: Dict[str, Any],
        question: str
    ) -> Dict[str, Any]:
        """Get career advice using AI."""
        if not self.is_available:
            return self._fallback_response("career_advisor")
        
        try:
            # Create career advice prompt
            prompt = PromptTemplate(
                input_variables=["context", "question"],
                template="""
                You are Dristhi, an AI career advisor for Indian students. 
                Provide personalized, practical career guidance based on the user's context.
                
                User Context: {context}
                Question: {question}
                
                Please provide:
                1. Direct answer to the question
                2. Actionable steps
                3. Relevant resources
                4. Encouragement and motivation
                
                Keep the response friendly, practical, and culturally relevant for Indian students.
                """
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Run the chain
            result = await asyncio.to_thread(
                chain.run,
                context=json.dumps(user_context, indent=2),
                question=question
            )
            
            return {
                "advice": result.strip(),
                "timestamp": datetime.utcnow().isoformat(),
                "model": self.model_name,
                "context_used": user_context
            }
            
        except Exception as e:
            logger.error(f"Error in career advisor: {e}")
            return self._fallback_response("career_advisor")
    
    async def finance_tips(
        self,
        user_context: Dict[str, Any],
        financial_question: str
    ) -> Dict[str, Any]:
        """Get financial advice using AI."""
        if not self.is_available:
            return self._fallback_response("finance_tips")
        
        try:
            # Create finance advice prompt
            prompt = PromptTemplate(
                input_variables=["context", "question"],
                template="""
                You are Dristhi, an AI financial advisor for Indian students. 
                Provide practical financial advice and tips based on the user's context.
                
                User Context: {context}
                Financial Question: {question}
                
                Please provide:
                1. Clear financial advice
                2. Practical tips for Indian students
                3. Budget-friendly suggestions
                4. Long-term financial planning
                5. Common mistakes to avoid
                
                Focus on practical, actionable advice suitable for students in India.
                """
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Run the chain
            result = await asyncio.to_thread(
                chain.run,
                context=json.dumps(user_context, indent=2),
                question=financial_question
            )
            
            return {
                "advice": result.strip(),
                "timestamp": datetime.utcnow().isoformat(),
                "model": self.model_name,
                "context_used": user_context
            }
            
        except Exception as e:
            logger.error(f"Error in finance tips: {e}")
            return self._fallback_response("finance_tips")
    
    async def motivation_nudge(
        self,
        user_context: Dict[str, Any],
        mood_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get motivational messages using AI."""
        if not self.is_available:
            return self._fallback_response("motivation_nudge")
        
        try:
            # Create motivation prompt
            prompt = PromptTemplate(
                input_variables=["context", "mood"],
                template="""
                You are Dristhi, an AI motivational coach for Indian students. 
                Provide personalized, uplifting motivation based on the user's context and mood.
                
                User Context: {context}
                Current Mood: {mood}
                
                Please provide:
                1. A personalized motivational message
                2. Specific encouragement based on their goals
                3. A small actionable step they can take today
                4. Cultural context that resonates with Indian students
                5. Positive reinforcement
                
                Make it warm, encouraging, and culturally relevant.
                """
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Run the chain
            result = await asyncio.to_thread(
                chain.run,
                context=json.dumps(user_context, indent=2),
                mood=mood_context or "general"
            )
            
            return {
                "motivation": result.strip(),
                "timestamp": datetime.utcnow().isoformat(),
                "model": self.model_name,
                "context_used": user_context
            }
            
        except Exception as e:
            logger.error(f"Error in motivation nudge: {e}")
            return self._fallback_response("motivation_nudge")
    
    async def habit_suggestion(
        self,
        user_context: Dict[str, Any],
        current_habits: List[str]
    ) -> Dict[str, Any]:
        """Get personalized habit suggestions using AI."""
        if not self.is_available:
            return self._fallback_response("habit_suggestion")
        
        try:
            # Create habit suggestion prompt
            prompt = PromptTemplate(
                input_variables=["context", "habits"],
                template="""
                You are Dristhi, an AI habit coach for Indian students. 
                Suggest personalized habits based on the user's context and current habits.
                
                User Context: {context}
                Current Habits: {habits}
                
                Please suggest:
                1. 2-3 new habits that would complement their current routine
                2. Why these habits would be beneficial
                3. How to start implementing them gradually
                4. Tips for maintaining consistency
                5. Cultural considerations for Indian students
                
                Make suggestions practical and achievable.
                """
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Run the chain
            result = await asyncio.to_thread(
                chain.run,
                context=json.dumps(user_context, indent=2),
                habits=", ".join(current_habits) if current_habits else "None"
            )
            
            return {
                "suggestions": result.strip(),
                "timestamp": datetime.utcnow().isoformat(),
                "model": self.model_name,
                "context_used": user_context
            }
            
        except Exception as e:
            logger.error(f"Error in habit suggestion: {e}")
            return self._fallback_response("habit_suggestion")
    
    async def personalized_insight(
        self,
        user_context: Dict[str, Any],
        insight_type: str = "general"
    ) -> Dict[str, Any]:
        """Get personalized insights using AI."""
        if not self.is_available:
            return self._fallback_response("personalized_insight")
        
        try:
            # Create insight prompt
            prompt = PromptTemplate(
                input_variables=["context", "type"],
                template="""
                You are Dristhi, an AI life coach for Indian students. 
                Provide personalized insights based on the user's context and the requested insight type.
                
                User Context: {context}
                Insight Type: {type}
                
                Please provide:
                1. A personalized observation about their progress
                2. Areas where they're doing well
                3. Potential areas for improvement
                4. Specific recommendations
                5. Encouragement and motivation
                
                Make it insightful, actionable, and culturally relevant.
                """
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Run the chain
            result = await asyncio.to_thread(
                chain.run,
                context=json.dumps(user_context, indent=2),
                type=insight_type
            )
            
            return {
                "insight": result.strip(),
                "timestamp": datetime.utcnow().isoformat(),
                "model": self.model_name,
                "context_used": user_context,
                "insight_type": insight_type
            }
            
        except Exception as e:
            logger.error(f"Error in personalized insight: {e}")
            return self._fallback_response("personalized_insight")
    
    def _fallback_response(self, service_type: str) -> Dict[str, Any]:
        """Provide fallback responses when AI is unavailable."""
        fallback_responses = {
            "career_advisor": {
                "advice": "I'm currently unavailable, but here's some general career advice: Focus on building practical skills, network actively, and stay updated with industry trends. Consider internships and projects to gain hands-on experience.",
                "timestamp": datetime.utcnow().isoformat(),
                "model": "fallback",
                "note": "AI service temporarily unavailable"
            },
            "finance_tips": {
                "advice": "While I'm unavailable, here are some basic financial tips: Create a budget, save regularly, avoid unnecessary debt, and start investing early. Consider using apps to track your expenses.",
                "timestamp": datetime.utcnow().isoformat(),
                "model": "fallback",
                "note": "AI service temporarily unavailable"
            },
            "motivation_nudge": {
                "motivation": "Remember, every small step counts towards your goals! Stay consistent, be patient with yourself, and celebrate your progress. You're capable of amazing things!",
                "timestamp": datetime.utcnow().isoformat(),
                "model": "fallback",
                "note": "AI service temporarily unavailable"
            },
            "habit_suggestion": {
                "suggestions": "Consider starting with simple habits like daily reading, exercise, or meditation. Start small and build consistency gradually. Remember, it's better to do a little consistently than a lot occasionally.",
                "timestamp": datetime.utcnow().isoformat(),
                "model": "fallback",
                "note": "AI service temporarily unavailable"
            },
            "personalized_insight": {
                "insight": "Focus on your strengths and work on areas that need improvement. Consistency is key to progress. Keep track of your achievements and learn from setbacks.",
                "timestamp": datetime.utcnow().isoformat(),
                "model": "fallback",
                "note": "AI service temporarily unavailable"
            }
        }
        
        return fallback_responses.get(service_type, fallback_responses["personalized_insight"])
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if self.llm:
                # Cleanup any resources if needed
                pass
            logger.info("AI service cleanup completed")
        except Exception as e:
            logger.error(f"Error during AI service cleanup: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get AI service status."""
        return {
            "available": self.is_available,
            "model": self.model_name,
            "base_url": self.ollama_base_url,
            "last_check": datetime.utcnow().isoformat()
        }
