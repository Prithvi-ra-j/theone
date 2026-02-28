"""Refactored AI service with Multi-Agent architecture."""

import json
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime
from loguru import logger
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama

from app.core.config import settings
from app.services.context_service import ContextService

class BaseAgent:
    """Base class for all specialized agents."""
    def __init__(self, llm: Any, model_name: str, language_instruction_func: Any):
        self.llm = llm
        self.model_name = model_name
        self._get_lang_instr = language_instruction_func

    def _format_context(self, user_context: Dict[str, Any], site_context: str) -> str:
        """Standardize context formatting for agents."""
        return (
            f"Feature Specific Context: {json.dumps(user_context)}\n"
            f"Global User Progress/Context: {site_context}"
        )

class CareerAgent(BaseAgent):
    """Specialized agent for career advice."""
    async def get_advice(self, user_context: Dict[str, Any], site_context: str, question: str, language: str, memory_context: str) -> str:
        lang_instr = self._get_lang_instr(language)
        context = self._format_context(user_context, site_context)
        prompt = PromptTemplate(
            input_variables=["context", "memory_context", "question", "lang_instruction"],
            template=(
                "You are the Dristhi Career Expert. {lang_instruction}\n\n"
                "Focus on career growth, skill-up roadmaps, and job market trends in India.\n"
                "Respond in Markdown with: ## Overview, ## Next 3 Steps, ## Resources.\n\n"
                "CONTEXT:\n{context}\n\n"
                "CONVERSATION HISTORY SUMMARY:\n{memory_context}\n\n"
                "LATEST QUESTION: {question}"
            )
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = await asyncio.to_thread(chain.run, context=context, memory_context=memory_context, question=question, lang_instruction=lang_instr)
        return str(result)

class FinanceAgent(BaseAgent):
    """Specialized agent for financial advice."""
    async def get_advice(self, user_context: Dict[str, Any], site_context: str, question: str, language: str, memory_context: str = "") -> str:
        lang_instr = self._get_lang_instr(language)
        context = self._format_context(user_context, site_context)
        prompt = PromptTemplate(
            input_variables=["context", "memory_context", "question", "lang_instruction"],
            template=(
                "You are the Dristhi Finance Expert. {lang_instruction}\n\n"
                "Focus on student budgeting, scholarship ROI, and smart saving in the Indian context.\n"
                "Respond in Markdown with: ## Financial Analysis, ## Actionable Tips.\n\n"
                "CONTEXT:\n{context}\n\n"
                "CONVERSATION HISTORY SUMMARY:\n{memory_context}\n\n"
                "QUESTION: {question}"
            )
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = await asyncio.to_thread(chain.run, context=context, memory_context=memory_context, question=question, lang_instruction=lang_instr)
        return str(result)

class WellnessAgent(BaseAgent):
    """Specialized agent for motivation and mental health."""
    async def get_advice(self, user_context: Dict[str, Any], site_context: str, question: str, language: str, memory_context: str = "") -> str:
        lang_instr = self._get_lang_instr(language)
        context = self._format_context(user_context, site_context)
        prompt = PromptTemplate(
            input_variables=["context", "memory_context", "question", "lang_instruction"],
            template=(
                "You are the Dristhi Wellness Buddy. {lang_instruction}\n\n"
                "Focus on motivation, exam stress management, and holistic growth for Indian students.\n"
                "Respond in Markdown with a warm, encouraging tone.\n\n"
                "CONTEXT:\n{context}\n\n"
                "CONVERSATION HISTORY:\n{memory_context}\n\n"
                "QUESTION: {question}"
            )
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = await asyncio.to_thread(chain.run, context=context, memory_context=memory_context, question=question, lang_instruction=lang_instr)
        return str(result)

class AIService:
    """Coordinator service for the Multi-Agent system."""
    def __init__(self):
        self.llm = None
        self.is_available = False
        self.model_name = "mock"
        self._init_llm()
        
        if self.is_available:
            try:
                self.career_agent = CareerAgent(self.llm, self.model_name, self._get_language_instruction)
            except Exception as e:
                logger.error(f"CareerAgent Init Failed: {e}")
                self.career_agent = None

            try:
                self.finance_agent = FinanceAgent(self.llm, self.model_name, self._get_language_instruction)
            except Exception as e:
                logger.error(f"FinanceAgent Init Failed: {e}")
                self.finance_agent = None

            try:
                self.wellness_agent = WellnessAgent(self.llm, self.model_name, self._get_language_instruction)
            except Exception as e:
                logger.error(f"WellnessAgent Init Failed: {e}")
                self.wellness_agent = None

    def _init_llm(self):
        # Re-using the logic from the old service but simplified for the demo
        try:
            if settings.LLM_PROVIDER == "api":
                self.llm = ChatOpenAI(
                    api_key=settings.API_LLM_API_KEY,
                    base_url=settings.API_LLM_BASE_URL,
                    model=settings.API_LLM_MODEL,
                )
                self.is_available = True
                self.model_name = settings.API_LLM_MODEL
            elif settings.LLM_PROVIDER == "ollama":
                 self.llm = Ollama(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
                 self.is_available = True
                 self.model_name = settings.OLLAMA_MODEL
        except Exception as e:
            logger.error(f"LLM Init Error: {e}")
            self.is_available = False

    async def _summarize_history(self, messages: List[Dict[str, str]]) -> str:
        """Use LLM to summarize conversation history."""
        if not messages: return ""
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        prompt = PromptTemplate(
            input_variables=["history"],
            template="Summarize the core context and progress of this conversation in 3-5 concise sentences:\n\n{history}"
        )
        try:
            chain = LLMChain(llm=self.llm, prompt=prompt)
            summary = await asyncio.to_thread(chain.run, history=history_text)
            return str(summary)
        except Exception as e:
            logger.error(f"History summarization failed: {e}")
            return "Continuing the conversation."

    async def _process_history(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Keep latest 8 messages and summarize the rest."""
        if len(messages) <= 8:
            return {"history": "\n".join([f"{m['role']}: {m['content']}" for m in messages]), "latest": messages}
        
        to_summarize = messages[:-8]
        latest = messages[-8:]
        summary = await self._summarize_history(to_summarize)
        return {"history": summary, "latest": latest}

    async def career_advisor(self, user_context: Dict[str, Any], question: str, language: str = "english", user_id: Optional[int] = None, db: Optional[Session] = None) -> Dict[str, Any]:
        """Route to CareerAgent with site awareness."""
        if not self.is_available or not getattr(self, "career_agent", None):
             return {"advice": "Dristhi Career AI is temporarily refining its knowledge. Please try again in a few moments."}
        
        site_context = ContextService.get_user_progress_summary(db, user_id) if db and user_id else "No platform data available yet."
        
        try:
            advice = await self.career_agent.get_advice(user_context, site_context, question, language, "Feature-specific query.")
            return {"advice": advice, "timestamp": datetime.utcnow().isoformat(), "model": self.model_name}
        except Exception as e:
            logger.error(f"CareerAdvisor Call Failed: {e}")
            # Fallback to LLM with simpler prompt instead of hardcoded string
            return {"advice": "I'm having trouble retrieving detailed advice right now, but please continue with your current goals!"}

    async def conversation(self, messages: List[Dict[str, str]], language: str = "english", user_id: Optional[int] = None, db: Optional[Session] = None) -> Dict[str, Any]:
        """Intelligent routing with summarizing memory and site awareness."""
        if not self.is_available:
            return {"response": "AI services are currently undergoing maintenance. I'll be back shortly!"}

        processed = await self._process_history(messages)
        memory_summary = processed["history"]
        last_msg = messages[-1]["content"].lower()
        site_context = ContextService.get_user_progress_summary(db, user_id) if db and user_id else "No platform data available yet."
        
        try:
            # Simple intent detection
            if any(w in last_msg for w in ["money", "salary", "finance", "budget", "fees", "scholarship"]):
                advice = await self.finance_agent.get_advice({}, site_context, last_msg, language, memory_summary)
            elif any(w in last_msg for w in ["stress", "sad", "unhappy", "tired", "motivation", "help"]):
                advice = await self.wellness_agent.get_advice({}, site_context, last_msg, language, memory_summary)
            else:
                advice = await self.career_agent.get_advice({}, site_context, last_msg, language, memory_summary)
                
            return {"response": advice}
        except Exception as e:
            logger.error(f"Conversation routing failed: {e}")
            return {"response": "I'm listening, but could you please rephrase that? I'm having a slight technical hiccup."}