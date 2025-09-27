Dristhi — Career Page AI Features: In-depth Analysis & Remediation (Expert Review)
Summary of this document

Purpose: review Career page AI surface end-to-end (frontend -> API -> backend LLM & memory), list what works, what is broken or risky, and provide precise fixes, verification steps, and next steps.
Contents:
Executive summary (high level)
Inventory & mapping (frontend → api module → backend endpoint)
Findings (what works, what’s broken/mismatched, conditional behaviors)
Concrete fixes (copy-paste patches/snippets)
How to run / verify locally (PowerShell commands)
Edge cases, risks, and recommended follow-ups
Short prioritized next steps
Executive summary
The backend has robust AI endpoints for career features: GET /career/feedback, POST /career/goals/{goal_id}/advice, GET /career/recommendations, and POST /career/generate-roadmap. They use a guarded AIService and MemoryService (FAISS + embeddings) and provide graceful fallbacks when AI or memory are unavailable.
The frontend mostly targets these endpoints, but there is at least one clear client-side bug: Career.jsx calls careerAPI.getAIFeedback() but getAIFeedback is not implemented in career.js. This prevents the "Get AI Feedback" button from working.
Other career AI features are wired correctly:
AI recommendations: AIRecommendations → careerAPI.getSkillRecommendations() → backend GET /career/recommendations (works with fallback).
Goal advice: careerAPI.postGoalAdvice(goalId, {question}) → backend POST /career/goals/{goal_id}/advice (works with RAG if memory configured).
RAG (memory) works when sentence-transformers + FAISS are available; otherwise the MemoryService gracefully falls back to DB keyword search.
AI availability at runtime depends on settings.ENABLE_AI_FEATURES, configured LLM_PROVIDER, API keys, and optionally AI_FORCE_FALLBACK.
Verdict: backend endpoints are implemented and defensively coded. Fix the missing client binding and optionally improve UX loading states and an AI-availability indicator for best user experience.

Inventory — files inspected (key)
Frontend
Career.jsx — Career page UI, AI advice modal, AI feedback button.
AIRecommendations.jsx — uses careerAPI.getSkillRecommendations().
TaskCard.jsx — exposes onAIAdvice button.
career.js — career API module (client).
ai.js — ai API module (many endpoints declared).
useCareer.js
Backend
career.py — career endpoints: /feedback, /recommendations, /goals/{id}/advice, /generate-roadmap, /tasks/{task_id}/complete, etc.
ai.py — conversation proxy POST /ai/conversation.
ai_service.py — LLM wrapper AIService with career_advisor, generate_tasks_for_goal, generate_feedback, init logic and robust fallback.
memory_service.py — MemoryService (sentence-transformers + FAISS), semantic_search, get_user_context.
career_service.py — CareerService.generate_roadmap, JSON parsing and RAG usage.
main.py — lifespan setup, ai_service and memory_service initialization.
Mapping: frontend call → career API module → backend endpoint
Career page "Get AI Feedback"

Frontend: careerAPI.getAIFeedback() (called in Career.jsx)
career module: MISSING (no getAIFeedback defined in career.js)
Backend endpoint: GET /career/feedback (exists in career.py)
Status: BROKEN on frontend (missing binding). Backend exists.
Goal-specific advice (AI modal)

Frontend: careerAPI.postGoalAdvice(goalId, { question })
career module: postGoalAdvice exists (maps to POST /career/goals/{goal_id}/advice)
Backend: POST /career/goals/{goal_id}/advice — implemented, uses ai_service.career_advisor, merges DB + memory (RAG) context, returns structured response or safe fallback.
Status: OK (server-side defensive)
AI Recommendations

Frontend: careerAPI.getSkillRecommendations() used by AIRecommendations component
career module: getSkillRecommendations exists (maps to GET /career/recommendations)
Backend: GET /career/recommendations — implemented, instructs LLM to return JSON-only format and parses it robustly (JSON direct, code fence extract, first JSON-like substring).
Status: OK (fallback provided if AI not configured)
Roadmap generation

Frontend: no explicit visible "generate roadmap" UX on the inspected Career.jsx file (endpoint exists but may not be called by the page).
Backend: POST /career/generate-roadmap implemented and delegates to CareerService.generate_roadmap (RAG + LLM).
Status: Server implemented; frontend may not call it yet.
ai API module vs backend

ai.js defines many /ai/... endpoints. Backend only reliably exposes POST /ai/conversation (in ai.py). Many /ai/* calls declared client-side may not have matching server handlers; prefer using career endpoints for career features.
Findings — details
Missing frontend API method for feedback

Career.jsx calls careerAPI.getAIFeedback() but career.js lacks that method. This will produce a runtime error or unhandled promise rejection when the user clicks the feedback button.
Backend career AI endpoints are defensive and robust

They use ai_service only when available. If AI service is not configured or initialization fails, endpoints return clear fallbacks instead of throwing 500s.
They use memory (RAG) where appropriate via memory_service, and fallback to DB keyword search if FAISS/embeddings aren't present.
LLM init & availability

AIService._init_llm depends on settings.LLM_PROVIDER and API keys. If keys are missing or provider unreachable, AIService.is_available will be False and endpoints return fallbacks.
app.main schedules ai_service.initialize() asynchronously so the app can start quickly; quick init attempts are made during request handling if needed.
Frontend ai module inconsistency

The ai.js client declares many endpoints that backend does not implement. This might cause future runtime errors if developers use aiAPI.* blindly.
JSON parsing heuristics

Backend attempts multiple parsing strategies to extract JSON from LLM output. Good for resilience; still not perfect if the LLM produces malformed JSON. Consider an extra validate-and-reprompt strategy if strict schema is required.
UX & performance

Long-running LLM calls need clear UX: loading indication, "queued" messages for long operations, cancellation/timeouts. The todo list already includes implementing loading states in UI components.
Concrete fixes (copy-paste)
A. Add getAIFeedback to the career client module

Open career.js and inside the exported careerAPI object add this one-liner (place next to other career API methods, e.g., near the Dashboard method):

B. (Recommended) Prefer career endpoints over aiJS for career features

If the frontend uses methods in ai.js for career-related features, switch to careerAPI equivalents (e.g., for goal advice use careerAPI.postGoalAdvice).
C. (Optional) Small UX improvement for Career page (example for AI feedback button)

If you want a minimal client change (in Career.jsx) to use a React Query style mutation (and show loading) — replace the manual handleGetAIFeedback with this pattern (pseudocode):

This uses React Query's built-in isLoading flag and is consistent with other mutations in the page.

D. (Optional) Add getAIServiceStatus endpoint or use /health

For better UX, consider adding a small client call that queries /health (already exists on the backend: GET /health) or a dedicated GET /api/v1/ai/status to show whether AI features are configured.
How to run & verify locally (PowerShell) — copy-paste commands
Backend dev server (PowerShell):
Frontend dev server (PowerShell):
Quick smoke test for the feedback endpoint (PowerShell curl):
If backend running at http://127.0.0.1:8001 and API base path is /api/v1:
Expected results:

If AI configured and available: JSON containing goal and feedback (advice text).
If AI not configured or forced fallback: fallback response like { "advice": "AI currently unavailable. Try again later." } or {"goal": "...", "feedback": "Keep going!"}.
After adding getAIFeedback to career.js, rebuild/start frontend and click the "Get AI Feedback" button on the Career page. Observe:
Button should not error for undefined function.
If backend responds, the AI Feedback block should populate.
If backend returns fallback, the UI should display that fallback.
Edge cases & risks
LLM output not valid JSON:
Backend attempts many heuristics to extract JSON. For stricter guarantees, implement validator + re-prompt ("I didn't get valid JSON; please return only JSON in the format X").
MemoryService dependencies:
sentence-transformers and faiss must be installed and embedding model available for semantic search. If missing, memory falls back to DB keyword search (less personalized).
Secrets & cost:
Ensure API keys are injected securely (env vars or secret manager). Remote LLM usage may incur costs — consider quotas/rate-limits.
Long-running operations:
Roadmap generation and complex RAG queries can take many seconds. Consider client-side timeouts and UX for queued processing.
Recommended follow-ups (prioritized)
High priority

Apply the one-line patch: add getAIFeedback to career.js (see “Concrete fixes” above). This resolves the immediate broken button.
Add frontend loading states for AI actions (use React Query isLoading for mutations). This is already in your todo and will prevent duplicate clicks and improve perceived performance.
Medium priority

Add a small AI availability indicator (call /health or a dedicated /api/v1/ai/status) in UI so users know whether to expect real AI responses or fallback.
Switch any aiAPI career calls to use careerAPI equivalents to avoid mismatches with backend.
Longer-term

Add a re-prompt-and-validate loop for strict JSON outputs from LLMs.
Automate FAISS seeding & embedding model setup in docs/CI for reproducible RAG behavior.
Add tests mocking ai_service to verify fallback and normal paths.
QA checklist (quick)
 Add getAIFeedback in career.js.
 Start backend & frontend dev servers.
 Click "Get AI Feedback" on Career page — confirm no console error.
 Confirm AI response appears (or fallback shown).
 Enable ENABLE_AI_FEATURES and configure LLM provider + keys to test real AI path.
 If you want RAG: install sentence-transformers + faiss and seed index (if a seeder script exists).
Short completion note & next action I can do for you
I prepared the above diagnostic and the exact code snippet to fix the missing getAIFeedback call. Next I can:

apply the frontend patch for you and run a quick smoke test, or
implement the loading states for Career page buttons (task complete, AI advice, generate-roadmap), or
add an AI status endpoint and small UI indicator.