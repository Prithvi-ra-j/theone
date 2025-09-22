"""AI service for LLM integration with LangChain."""

import json
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chains import LLMChain
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from app.core.config import settings


class AIService:
    def generate_tasks_for_goal(self, goal_title: str, goal_description: str) -> list:
        """Generate actionable tasks for a career goal using the LLM."""
        fallback = [
            {"title": "Define your first milestone", "description": "Break your goal into smaller steps."}
        ]
        if not self.llm:
            return fallback
        prompt = f"Generate a list of 5 actionable tasks to help achieve the following career goal: {goal_title}. Context: {goal_description}. Return as a JSON list of objects with 'title' and 'description'."
        try:
            # Support different LLM client interfaces
            if callable(self.llm):
                result = self.llm(prompt)
            elif hasattr(self.llm, "invoke"):
                result = self.llm.invoke(prompt)
            elif hasattr(self.llm, "generate"):
                # Some LLM clients use generate and return an object
                gen = self.llm.generate([prompt])
                # Attempt to extract string
                result = str(gen) if gen is not None else None
            else:
                result = None

            if not result:
                return fallback

            # Try to parse JSON from result
            try:
                tasks = json.loads(result)
                if isinstance(tasks, list):
                    return tasks
            except Exception:
                # Not JSON, return best-effort wrapper
                return [{"title": "Review AI output", "description": str(result)}]
        except Exception as e:
            logger.error(f"Error generating tasks: {e}")
            return fallback

    def generate_feedback(self, goal_title: str, completed_tasks: list) -> str:
        """Generate AI feedback on progress for a career goal."""
        fallback = "Keep going!"
        if not self.llm:
            return fallback
        prompt = f"User's goal: {goal_title}. Completed tasks: {completed_tasks}. Provide feedback and next steps."
        try:
            if callable(self.llm):
                feedback = self.llm(prompt)
            elif hasattr(self.llm, "invoke"):
                feedback = self.llm.invoke(prompt)
            elif hasattr(self.llm, "generate"):
                gen = self.llm.generate([prompt])
                feedback = str(gen) if gen is not None else None
            else:
                feedback = None

            return str(feedback) if feedback else fallback
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            return fallback
    """AI service for LLM integration."""
    
    def __init__(self):
        """Initialize AI service."""
        self.llm = None
        self.is_available = False
        self.model_name = None
        # Defer heavy initialization to an explicit async initialize() call
        # to avoid blocking the main thread during startup.
    
    def _init_llm(self) -> None:
        """Initialize LLM connection."""
        try:
            # If the developer requests forcing fallback mode, don't attempt
            # to connect to any external LLM provider.
            if settings.AI_FORCE_FALLBACK:
                logger.info("AI_FORCE_FALLBACK is set - using fallback responses only")
                self.is_available = False
                return
            if settings.LLM_PROVIDER == "ollama":
                # Test Ollama connection
                with httpx.Client(timeout=5.0) as client:
                    response = client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                    if response.status_code == 200:
                        self.is_available = True
                        self.llm = Ollama(
                            base_url=settings.OLLAMA_BASE_URL,
                            model=settings.OLLAMA_MODEL,
                            temperature=0.7
                        )
                        self.model_name = settings.OLLAMA_MODEL
                        logger.info(f"✅ Ollama connected successfully with model: {self.model_name}")
                    else:
                        logger.warning(f"⚠️ Ollama connection failed: {response.status_code}")
            elif settings.LLM_PROVIDER == "api":
                # Verify API key is available before initializing
                if not settings.API_LLM_API_KEY:
                    logger.error("❌ API LLM API key is not set")
                    self.is_available = False
                    return
                    
                try:
                    self.llm = ChatOpenAI(
                        api_key=settings.API_LLM_API_KEY,
                        base_url=settings.API_LLM_BASE_URL,
                        model=settings.API_LLM_MODEL,
                        temperature=0.7
                    )
                    # Test the connection with a simple query
                    _ = self.llm.invoke("Test connection")
                    self.model_name = settings.API_LLM_MODEL
                    self.is_available = True
                    logger.info(f"✅ API LLM connected successfully with model: {self.model_name}")
                except Exception as e:
                    logger.error(f"❌ API LLM connection error: {e}")
                    self.is_available = False
            elif settings.LLM_PROVIDER == "gemini":
                # If a Gemini API key is provided, consider the gemini provider available.
                # Optionally do a lightweight health check to validate the base URL.
                if settings.GEMINI_API_KEY:
                    try:
                        with httpx.Client(timeout=5.0) as client:
                            # A simple GET to the base URL to verify reachability (some Gemini
                            # deployments may not expose a root GET; ignore non-200 results).
                            _ = client.get(settings.GEMINI_BASE_URL)
                    except Exception:
                        # Non-fatal: we still mark provider available if key exists.
                        logger.debug("Gemini base URL health check failed; continuing because key exists")

                    self.is_available = True
                    self.model_name = settings.GEMINI_MODEL
                    logger.info(f"✅ Gemini configured (model={self.model_name}); will use REST API")
                else:
                    logger.warning("Gemini provider selected but GEMINI_API_KEY is not set")
                    self.is_available = False
            else:
                logger.error(f"❌ Invalid LLM_PROVIDER: {settings.LLM_PROVIDER}")
                self.is_available = False

        except Exception as e:
            logger.error(f"❌ LLM connection error: {e}")
            self.is_available = False

    async def initialize(self) -> None:
        """Asynchronously run _init_llm in a thread to avoid blocking.

        Call this from an async startup handler (e.g., the FastAPI lifespan)
        so LLM initialization runs in the background.
        """
        try:
            await asyncio.to_thread(self._init_llm)
        except Exception as e:
            logger.error(f"❌ Error during async initialize: {e}")
    
    async def career_advisor(
        self,
        user_context: Dict[str, Any],
        question: str,
        temperature: Optional[float] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get career advice using AI."""
        # If the service is not available or developer wanted fallback, return
        # the built-in fallback response instead of attempting a remote call.
        if not self.is_available or settings.AI_FORCE_FALLBACK:
            return self._fallback_response("career_advisor")
        
        try:
            # Get relevant memories using semantic search if user_id is provided
            memory_context = ""
            if user_id is not None:
                try:
                    from app.services.memory_service import MemoryService
                    memory_service = MemoryService()
                    
                    # Use semantic search to find relevant memories
                    relevant_memories = memory_service.semantic_search(
                        user_id=user_id,
                        query=question,
                        memory_type="career",
                        top_k=5
                    )
                    
                    # Extract memory content for context enhancement
                    if relevant_memories:
                        memory_context = "Relevant user information:\n"
                        for i, memory in enumerate(relevant_memories):
                            memory_context += f"- {memory.get('content', '')}"
                            if memory.get('description'):
                                memory_context += f": {memory.get('description', '')}"
                            memory_context += "\n"
                except Exception as mem_err:
                    logger.error(f"Error retrieving memories: {mem_err}")
            
            # Create career advice prompt with enhanced context
            prompt = PromptTemplate(
                input_variables=["context", "memory_context", "question"],
                template="""
                You are Dristhi, an AI career advisor for Indian students. 
                Provide personalized, practical career guidance based on the user's context.
                
                User Context: {context}
                
                User Memory Context: {memory_context}
                
                Question: {question}
                
                Please provide:
                1. Direct answer to the question
                2. Actionable steps
                3. Relevant resources
                4. Encouragement and motivation
                
                Keep the response friendly, practical, and culturally relevant for Indian students.
                """
            )
            
            # Allow callers to override temperature for deterministic outputs
            llm_to_use = self.llm
            if temperature is not None:
                try:
                    if settings.LLM_PROVIDER == "api":
                        # Create a temporary ChatOpenAI with the requested temperature
                        llm_to_use = ChatOpenAI(
                            api_key=settings.API_LLM_API_KEY,
                            base_url=settings.API_LLM_BASE_URL,
                            model=settings.API_LLM_MODEL,
                            temperature=temperature,
                        )
                    elif settings.LLM_PROVIDER == "ollama":
                        llm_to_use = Ollama(
                            base_url=settings.OLLAMA_BASE_URL,
                            model=settings.OLLAMA_MODEL,
                            temperature=temperature,
                        )
                except Exception as _:
                    # Fall back to the configured llm if temporary creation fails
                    llm_to_use = self.llm

            chain = LLMChain(llm=llm_to_use, prompt=prompt)
            
            # Run the chain
            result = await asyncio.to_thread(
                chain.run,
                context=json.dumps(user_context, indent=2),
                memory_context=memory_context if memory_context else "No additional memory context available.",
                question=question
            )
            
            return {
                "advice": result.strip(),
                "timestamp": datetime.utcnow().isoformat(),
                "model": self.model_name,
                "context_used": user_context,
                "enhanced_with_rag": bool(memory_context)
            }
            
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg and "No auth credentials found" in error_msg:
                logger.error(f"Authentication error in career advisor: {e}")
                # Update the fallback response to indicate auth issue
                fallback = self._fallback_response("career_advisor")
                fallback["advice"] = "AI service authentication error. Please check API credentials."
                fallback["note"] = "Authentication failed"
                return fallback
            else:
                logger.error(f"Error in career advisor: {e}")
                return self._fallback_response("career_advisor")
    
    async def finance_tips(
        self,
        user_context: Dict[str, Any],
        financial_question: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get financial advice using AI."""
        if not self.is_available:
            return self._fallback_response("finance_tips")
        
        try:
            # Get relevant memories using semantic search if user_id is provided
            memory_context = ""
            if user_id is not None:
                try:
                    from app.services.memory_service import MemoryService
                    memory_service = MemoryService()
                    
                    # Use semantic search to find relevant memories
                    relevant_memories = memory_service.semantic_search(
                        user_id=user_id,
                        query=financial_question,
                        memory_type="finance",
                        top_k=5
                    )
                    
                    # Extract memory content for context enhancement
                    if relevant_memories:
                        memory_context = "Relevant financial information:\n"
                        for i, memory in enumerate(relevant_memories):
                            memory_context += f"- {memory.get('content', '')}"
                            if memory.get('description'):
                                memory_context += f": {memory.get('description', '')}"
                            memory_context += "\n"
                except Exception as mem_err:
                    logger.error(f"Error retrieving memories: {mem_err}")
            
            # Create finance advice prompt
            prompt = PromptTemplate(
                input_variables=["context", "memory_context", "question"],
                template="""
                You are Dristhi, an AI financial advisor for Indian students. 
                Provide practical financial advice and tips based on the user's context.
                
                User Context: {context}
                User Memory Context: {memory_context}
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
                memory_context=memory_context if memory_context else "No additional memory context available.",
                question=financial_question
            )
            
            return {
                "advice": result.strip(),
                "timestamp": datetime.utcnow().isoformat(),
                "model": self.model_name,
                "context_used": user_context,
                "enhanced_with_rag": bool(memory_context)
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

    async def conversation(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Run a conversation using the configured LLM provider.

        messages: list of {role: 'user'|'system'|'assistant', 'content': '...'}
        """
        if not self.is_available:
            return {"error": "LLM unavailable", "fallback": True}

        # If provider is gemini, call Google Generative Language API
        if settings.LLM_PROVIDER == "gemini":
            try:
                import httpx

                prompt = "\n".join([m.get("content", "") for m in messages if m.get("role") in ("user", "system")])

                # Candidate endpoint patterns to try (order matters)
                candidates = [
                    f"{settings.GEMINI_BASE_URL}/{settings.GEMINI_MODEL}:generateText",
                    f"{settings.GEMINI_BASE_URL}/{settings.GEMINI_MODEL}:generate",
                    f"{settings.GEMINI_BASE_URL}/models/{settings.GEMINI_MODEL}:generateText",
                    f"{settings.GEMINI_BASE_URL}/models/{settings.GEMINI_MODEL}:generate",
                    f"{settings.GEMINI_BASE_URL}/models:generate",
                    f"{settings.GEMINI_BASE_URL}/models:generateText",
                ]

                headers = {}
                # Prefer API key as `key` query param (common for simple REST setups),
                # but also allow passing as Authorization header in case the endpoint expects it.
                params = {"key": settings.GEMINI_API_KEY} if settings.GEMINI_API_KEY else None

                async with httpx.AsyncClient(timeout=30.0) as client:
                    last_error = None
                    for url in candidates:
                        try:
                            # Choose payload shape depending on endpoint style
                            if url.endswith(":generate") or url.endswith(":generateText"):
                                payload = {"prompt": {"text": prompt}}
                            else:
                                # models:generate style expects model + prompt
                                payload = {"model": settings.GEMINI_MODEL, "prompt": {"text": prompt}}

                            r = await client.post(url, json=payload, params=params, headers=headers)
                            # If unauthorized or not found, try the next candidate
                            if r.status_code == 404:
                                last_error = f"404 for {url}"
                                continue
                            r.raise_for_status()
                            data = r.json()

                            # Try to extract text from several possible shapes
                            text = ""
                            # 1) candidates -> output/content
                            if isinstance(data.get("candidates"), list) and data.get("candidates"):
                                cand = data["candidates"][0]
                                text = cand.get("output") or cand.get("content", {}).get("text") or ""
                            # 2) output -> text
                            if not text and isinstance(data.get("output"), dict):
                                text = data.get("output", {}).get("text", "")
                            # 3) direct string
                            if not text and isinstance(data, str):
                                text = data

                            return {"response": text, "raw": data, "used_url": url}

                        except httpx.HTTPStatusError as he:
                            last_error = str(he)
                            continue
                        except Exception as e:
                            last_error = str(e)
                            continue

                    # If all candidates failed, return the last error encountered
                    return {"error": last_error or "unknown_error"}
            except Exception as e:
                logger.error(f"Error calling Gemini API: {e}")
                return {"error": str(e)}

        # Otherwise, try using existing LLM chain (sync wrapper)
        try:
            chain_prompt = "\n".join([m.get("content", "") for m in messages])
            if self.llm is None:
                return {"error": "llm_not_configured"}
            # Run chain synchronously in a thread for compatibility
            from langchain.chains import LLMChain

            prompt = PromptTemplate(input_variables=["text"], template="{text}")
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = await asyncio.to_thread(chain.run, text=chain_prompt)
            return {"response": result}
        except Exception as e:
            logger.error(f"Error running conversation chain: {e}")
            return {"error": str(e)}
    
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
            "provider": settings.LLM_PROVIDER,
            "model": self.model_name,
            "last_check": datetime.utcnow().isoformat()
        }