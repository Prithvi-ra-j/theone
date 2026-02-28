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
from app.services.eval_service import EvalService
from app.services.guardrail_service import GuardrailService

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
    """Coordinator service for the Multi-Agent system with Eval & Guardrails."""
    def __init__(self):
        self.llm = None
        self.is_available = False
        self.model_name = "mock"
        
        # New services integration
        self.eval_service = EvalService()
        self.guardrail_service = GuardrailService()
        
        self._init_llm()
        
        if self.is_available:
            self._init_agents()

    def _init_agents(self):
        """Initialize specialized agents."""
        try:
            self.career_agent = CareerAgent(self.llm, self.model_name, self._get_language_instruction)
            self.finance_agent = FinanceAgent(self.llm, self.model_name, self._get_language_instruction)
            self.wellness_agent = WellnessAgent(self.llm, self.model_name, self._get_language_instruction)
        except Exception as e:
            logger.error(f"Agent Initialization Failed: {e}")

    def _get_language_instruction(self, language: str) -> str:
        """Helper to get language specific instruction."""
        return f"Respond in {language.capitalize()} language."

    def _init_llm(self):
        # Re-using the logic from settings
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
        mask_sensitive = lambda text: self.guardrail_service.sanitize_pii(text)
        
        if len(messages) <= 8:
            cleaned = [{"role": m["role"], "content": mask_sensitive(m["content"])} for m in messages]
            return {"history": "\n".join([f"{m['role']}: {m['content']}" for m in cleaned]), "latest": cleaned}
        
        to_summarize = messages[:-8]
        latest = messages[-8:]
        summary = await self._summarize_history(to_summarize)
        return {"history": mask_sensitive(summary), "latest": latest}

    async def conversation(self, messages: List[Dict[str, str]], language: str = "english", user_id: Optional[int] = None, db: Any = None) -> Dict[str, Any]:
        """Agentic RAG Loop: Guardrail -> Routing -> Generate -> Eval -> (Self-Correct) -> Response."""
        if not self.is_available:
            return {"response": "AI services are currently undergoing maintenance. I'll be back shortly!"}

        # 1. Guardrail: Validate Input
        last_msg = messages[-1]["content"]
        guard_result = self.guardrail_service.validate_input(last_msg)
        if not guard_result["is_safe"]:
            return {"response": self.guardrail_service.get_guardrail_advice_fallback(guard_result["reason"])}

        # 2. Context & Routing
        processed = await self._process_history(messages)
        memory_summary = processed["history"]
        site_context = ContextService.get_user_progress_summary(db, user_id) if db and user_id else "No platform data available yet."
        
        last_msg_clean = last_msg.lower()
        
        try:
            # 3. Initial Generation
            if any(w in last_msg_clean for w in ["money", "salary", "finance", "budget", "fees", "scholarship"]):
                advice = await self.finance_agent.get_advice({}, site_context, last_msg, language, memory_summary)
            elif any(w in last_msg_clean for w in ["stress", "sad", "unhappy", "tired", "motivation", "help"]):
                advice = await self.wellness_agent.get_advice({}, site_context, last_msg, language, memory_summary)
            else:
                advice = await self.career_agent.get_advice({}, site_context, last_msg, language, memory_summary)
            
            # 4. Evaluation (Internal)
            scores = await self.eval_service.score_response(last_msg, site_context, advice)
            
            # 5. Agentic Self-Correction Loop
            # If completeness is low (missing headers), trigger a correction
            if scores["completeness"] < 1.0:
                logger.info(f"Self-Correction Triggered: Completeness score {scores['completeness']}")
                correction_prompt = f"The previous response was good but skipped required Markdown formatting. Please provide the same advice but ensure you use '## Overview' and '## Next Steps' headers.\n\nPREVIOUS RESPONSE:\n{advice}"
                
                # Re-run with the correction prompt
                advice = await self.career_agent.get_advice({}, site_context, correction_prompt, language, memory_summary)
                # Re-eval
                scores = await self.eval_service.score_response(last_msg, site_context, advice)

            # 6. Final Guardrail: Validate Output
            if not self.guardrail_service.validate_output(advice):
                return {"response": "The AI generated an inappropriate response. Let's try rephrasing your goal."}

            return {
                "response": advice,
                "metrics": {
                    "faithfulness": scores["faithfulness"],
                    "relevance": scores["relevance"],
                    "completeness": scores["completeness"],
                    "agg_quality": scores["aggregate_score"]
                }
            }
        except Exception as e:
            logger.error(f"Conversation routing or Eval failed: {e}")
            return {"response": "I'm having a slight technical hiccup. Please try rephrasing!"}
