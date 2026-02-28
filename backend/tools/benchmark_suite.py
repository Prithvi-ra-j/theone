"""
Benchmark suite for Dristhi AI.
Runs 'Golden Questions' against the AIService and reports quality metrics.
"""

import asyncio
import json
from typing import List, Dict
from loguru import logger
import sys
import os

# Add backend to path so we can import app
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.ai_service import AIService

GOLDEN_QUESTIONS = [
    {
        "category": "Career",
        "question": "I am a 2nd year B.Tech student interested in AI. What should be my next 3 steps?",
        "expected_themes": ["internship", "projects", "python", "courses"]
    },
    {
        "category": "Finance",
        "question": "How can I save money on my hostel fees in Bangalore?",
        "expected_themes": ["budget", "sharing", "scholarship", "expenses"]
    },
    {
        "category": "Wellness",
        "question": "I feel very stressed about my upcoming semester exams. Help me.",
        "expected_themes": ["breathe", "schedule", "break", "support"]
    }
]

async def run_benchmarks():
    print("🚀 Starting Dristhi AI Benchmark Suite...")
    ai_service = AIService()
    
    if not ai_service.is_available:
        print("❌ AI Service not available. Check Ollama or API keys.")
        return

    results = []
    
    for item in GOLDEN_QUESTIONS:
        print(f"\nTesting [{item['category']}]: {item['question']}")
        
        # Simulate a conversation with a single message
        messages = [{"role": "user", "content": item["question"]}]
        
        try:
            response_data = await ai_service.conversation(messages)
            
            # Extract metrics from response
            metrics = response_data.get("metrics", {})
            agg_quality = metrics.get("agg_quality", 0.0)
            
            print(f"✅ Response received. Quality Score: {agg_quality}")
            
            results.append({
                "category": item["category"],
                "question": item["question"],
                "score": agg_quality,
                "metrics": metrics,
                "status": "PASS" if agg_quality > 0.7 else "FAIL"
            })
        except Exception as e:
            print(f"❌ Test failed for {item['category']}: {e}")
            results.append({"category": item["category"], "status": "ERROR", "error": str(e)})

    # Final Report
    print("\n" + "="*40)
    print("📊 BENCHMARK REPORT")
    print("="*40)
    
    total_score = 0
    for r in results:
        status_icon = "🟢" if r["status"] == "PASS" else "🔴"
        print(f"{status_icon} [{r['category']}] Score: {r.get('score', 'N/A')}")
        if r["status"] == "PASS":
            total_score += 1
            
    print(f"\nFinal Accuracy: {total_score}/{len(results)} ({(total_score/len(results))*100:.1f}%)")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
