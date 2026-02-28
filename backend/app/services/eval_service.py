"""Service for evaluating AI output quality (Faithfulness, Relevance, etc.)."""

import re
from typing import Any, Dict, List, Optional
from loguru import logger
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama

from app.core.config import settings

class EvalService:
    """Evaluates LLM responses for quality and accuracy."""

    def __init__(self, llm: Any = None):
        self.llm = llm or self._init_default_llm()

    def _init_default_llm(self):
        """Standard LLM init for evaluation (often a cheaper/faster model)."""
        try:
            if settings.LLM_PROVIDER == "api":
                return ChatOpenAI(
                    api_key=settings.API_LLM_API_KEY,
                    base_url=settings.API_LLM_BASE_URL,
                    model=settings.API_LLM_MODEL,
                )
            elif settings.LLM_PROVIDER == "ollama":
                return Ollama(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
        except Exception as e:
            logger.error(f"EvalService LLM Init Failed: {e}")
            return None

    def calculate_faithfulness(self, context: str, response: str) -> float:
        """
        Heuristic-based faithfulness check.
        In a full implementation, this uses an LLM-as-a-judge prompt.
        For MVP, we check overlap of key entities/terms.
        """
        if not context or not response:
            return 0.0
        
        # Simple word-overlap as a baseline heuristic
        context_words = set(re.findall(r'\w+', context.lower()))
        response_words = set(re.findall(r'\w+', response.lower()))
        
        # We only care about words in the response that are ALSO in the context
        # (excluding very common stopwords)
        stopwords = {"the", "is", "at", "which", "on", "and", "a", "an", "of", "to", "in", "it"}
        important_response_words = response_words - stopwords
        
        matches = important_response_words.intersection(context_words)
        
        if not important_response_words:
            return 1.0
            
        return len(matches) / len(important_response_words)

    async def score_response(self, prompt: str, context: str, response: str) -> Dict[str, float]:
        """
        Comprehensive scoring suite.
        Returns: {faithfulness, relevance, completeness}
        """
        faithfulness = self.calculate_faithfulness(context, response)
        
        # LLM-based Relevance check (Simulated for speed, but ready for prompt-based grading)
        relevance = 0.9 if len(response) > 50 else 0.5 
        
        # Completeness check (Does it have the required Markdown headers?)
        has_headers = 1.0 if "##" in response else 0.0
        
        return {
            "faithfulness": round(faithfulness, 2),
            "relevance": relevance,
            "completeness": has_headers,
            "aggregate_score": round((faithfulness + relevance + has_headers) / 3, 2)
        }

    @staticmethod
    def get_eval_prompt_template() -> PromptTemplate:
        """Template for LLM-as-a-judge evaluation."""
        return PromptTemplate(
            input_variables=["context", "response"],
            template=(
                "Evaluate the following response based ONLY on the provided context.\n"
                "Score from 0 to 1 based on how much of the response is supported by the context.\n"
                "Return ONLY a float number.\n\n"
                "CONTEXT:\n{context}\n\n"
                "RESPONSE:\n{response}"
            )
        )
