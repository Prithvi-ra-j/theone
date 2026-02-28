"""Reality service for failure-proofing career paths and family alignment."""

from typing import Any, Dict, List, Optional
from loguru import logger

class RealityService:
    def __init__(self, ai_service: Any):
        self.ai = ai_service

    async def generate_plan_b(self, primary_goal: str, language: str = "english") -> str:
        """Generate a backup career path if the primary one fails."""
        prompt = (
            f"The user's primary goal is '{primary_goal}'. This is a high-stakes path (like JEE, UPSC, or pre-med). "
            "Generate a 'Plan B' roadmap: a parallel skill set they should build as a backup. "
            "Format as Markdown with '## Why this Plan B' and '## Next 3 Skill-Up Steps'. "
            "Make it culturally relevant to the Indian context."
        )
        
        try:
            # We use the career_advisor logic but with a specialized prompt
            result = await self.ai.career_advisor(
                user_context={"primary_goal": primary_goal, "type": "failure_recovery"},
                question=prompt,
                language=language
            )
            return result.get("advice", "Backup plan could not be generated at this time.")
        except Exception as e:
            logger.exception("Error generating Plan B")
            return "Focus on building transferable skills like coding or digital design while pursuing your main goal."

    async def generate_parent_report(self, career_path: str, projected_salary: str, language: str = "hindi") -> str:
        """Generate a report aimed at Indian parents to explain a student's career choice."""
        prompt = (
            f"A student wants to pursue '{career_path}' with a projected starting salary of '{projected_salary}'. "
            "Generate a 'Communication Toolkit' for their parents. "
            "Explain: 1. Why this is a stable and respectable career. 2. Real-world examples of success. 3. Financial security. "
            "USE SIMPLE, NON-TECHNICAL LANGUAGE. Emphasize respectability and growth."
        )
        
        try:
            # We default to Hindi for parent reports as requested in the roadmap
            result = await self.ai.career_advisor(
                user_context={"career_path": career_path, "target_audience": "Indian Parents"},
                question=prompt,
                language=language
            )
            return result.get("advice", "Parent report could not be generated.")
        except Exception as e:
            logger.exception("Error generating Parent Report")
            return "This career path has high growth potential and financial stability in the current Indian economy."
