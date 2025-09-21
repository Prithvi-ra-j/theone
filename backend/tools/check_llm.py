"""
LLM connectivity checker for Dristhi backend (OpenRouter edition).

Usage (PowerShell):
# 1. Add your API settings to backend/.env (copy from backend/env.example). Example entries:
#    LLM_PROVIDER=api
#    API_LLM_API_KEY=your_openrouter_api_key_here
#    API_LLM_BASE_URL=https://openrouter.ai/api/v1
#    API_LLM_MODEL=x-ai/grok-4-fast:free
#    AI_FORCE_FALLBACK=false
#
# 2. Activate your virtualenv and install dependencies:
#    python -m venv .venv311
#    .\.venv311\Scripts\Activate.ps1
#    pip install -r requirements.txt
#
# 3. Run the checker:
#    python backend\tools\check_llm.py
"""

import asyncio
import os
import sys
from loguru import logger

# Ensure backend package is importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.core.config import settings
from app.services.ai_service import AIService


async def main():
    logger.info("Starting LLM connectivity check")

    # Print environment variables for sanity check
    print("Configured LLM settings:")
    print(f"  Provider       : {settings.LLM_PROVIDER}")
    print(f"  Base URL       : {settings.API_LLM_BASE_URL}")
    print(f"  Model          : {settings.API_LLM_MODEL}")
    print(f"  Force Fallback : {settings.AI_FORCE_FALLBACK}")

    if not settings.API_LLM_API_KEY or "sk-" not in settings.API_LLM_API_KEY:
        print("\n❌ Missing or invalid OpenRouter API key! Check API_LLM_API_KEY in backend/.env")
        return 1

    svc = AIService()

    # Initialize LLM service
    await svc.initialize()

    status = svc.get_status()
    print("\nLLM Status:")
    for k, v in status.items():
        print(f"  {k}: {v}")

    if not svc.is_available:
        print(
            "\n❌ LLM not available. If you intended to use a remote provider, "
            "verify your settings in backend/.env and ensure AI_FORCE_FALLBACK "
            "is not set to true."
        )
        print("Check LLM_PROVIDER, API_LLM_BASE_URL, API_LLM_MODEL, and API keys.")
        return 1

    # Run a small smoke prompt to check end-to-end
    user_context = {
        "user_id": 0,
        "goals": [{"id": 1, "title": "Test Goal", "status": "active"}],
        "skills": [],
    }
    prompt = "Give one short recommended next skill for this user in one sentence. Return only the sentence."

    try:
        print("\nSending test prompt to the model...")
        result = await svc.career_advisor(user_context, prompt)
        print("\n✅ Sample prompt result:")
        print(result)
        return 0
    except Exception as e:
        logger.exception("Error during sample prompt: %s", e)
        return 2


if __name__ == "__main__":
    code = asyncio.run(main())
    sys.exit(code)
