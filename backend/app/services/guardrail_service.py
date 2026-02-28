"""Service for AI Safety Guardrails (Injection detection, Topical alignment, PII masking)."""

import re
from typing import Any, Dict, List, Optional
from loguru import logger

class GuardrailService:
    """Provides security and policy enforcement for AI interactions."""

    def __init__(self):
        # Common prompt injection patterns
        self.injection_patterns = [
            r"ignore all previous instructions",
            r"system: ",
            r"you are now a",
            r"forget your current instructions",
            r"DAN mode",
            r"do anything now",
            r"stop being",
            r"bypass the"
        ]
        
        # Off-topic keywords (very simple heuristic for demonstration)
        self.off_topic_patterns = [
            r"betting", r"gambling", r"crypto scam", r"hack into",
            r"illegal", r"steal", r"nude", r"porn"
        ]

    def validate_input(self, text: str) -> Dict[str, Any]:
        """Check if the user input is safe and within scope."""
        low_text = text.lower()
        
        # 1. Check for prompt injection
        for pattern in self.injection_patterns:
            if re.search(pattern, low_text):
                logger.warning(f"Guardrail: Potential injection detected in input: {text[:50]}...")
                return {"is_safe": False, "reason": "System policy violation (potential injection)."}
        
        # 2. Check for harmful/off-topic content
        for pattern in self.off_topic_patterns:
            if re.search(pattern, low_text):
                logger.warning(f"Guardrail: Harmful content detected in input: {pattern}")
                return {"is_safe": False, "reason": "Inappropriate or off-topic content."}
                
        return {"is_safe": True}

    def sanitize_pii(self, text: str) -> str:
        """Mask potential PII like emails, phones, and Aadhaar numbers (Indian context)."""
        # Email
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_MASKED]', text)
        
        # Phone (India format)
        text = re.sub(r'\b(?:\+91|0)?[6789]\d{9}\b', '[PHONE_MASKED]', text)
        
        # Aadhaar (XXXX XXXX XXXX)
        text = re.sub(r'\b\d{4}\s\d{4}\s\d{4}\b', '[ID_MASKED]', text)
        
        return text

    def validate_output(self, response: str) -> bool:
        """Ensure the AI hasn't generated something toxic or wildly off-topic."""
        low_response = response.lower()
        
        # Basic check for toxic vocabulary (demo level)
        for pattern in self.off_topic_patterns:
            if re.search(pattern, low_response):
                logger.error(f"Guardrail: AI generated toxic content: {pattern}")
                return False
                
        return True

    def get_guardrail_advice_fallback(self, reason: str) -> str:
        """Standard fallback response if guardrail triggers."""
        return (
            f"I cannot process this request because it violates Dristhi safety policies: {reason}\n\n"
            "Please focus your queries on career growth, student finance, or mental well-being."
        )
