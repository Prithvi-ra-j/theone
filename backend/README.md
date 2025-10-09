# Backend - Quick run & debugging guide

This file contains short instructions to get the backend running locally for development and to help verify the API endpoints.

Prereqs (recommended)
- Python 3.11 (3.11.x)
- PostgreSQL running and accessible via DATABASE_URL in `backend/.env` or environment
- A virtualenv (see below)

1) Create and activate a venv (PowerShell)

   python -m venv .venv311; .\.venv311\Scripts\Activate.ps1

2) Install dependencies

   pip install -r requirements.txt

3) Ensure DB schema is updated (SQLite default)

Option A (recommended): run alembic upgrade

   cd backend
   .\.venv311\Scripts\python.exe -m alembic upgrade head

Option B (quick fix): run the provided script to ALTER the table directly

   python backend\tools\ensure_career_category_nullable.py

4) Start the backend (from workspace root)

   .\.venv311\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

5) Verify endpoints

   python backend\tools\endpoint_checker.py --base http://localhost:8000/api/v1

Notes & troubleshooting
- If you see NotNullViolation on careergoal.category during POST, run the DB fix (step 3) and restart the server.
- If CORS preflight (OPTIONS) returns 400, ensure BACKEND_CORS_ORIGINS in `backend/.env` contains your frontend origin (e.g. http://localhost:5173) and restart the server.
- By default the app uses SQLite at `backend/data/app.db`. To use Postgres, set `DATABASE_URL` accordingly in env and redeploy.
- Use the endpoint checker to quickly validate which endpoints are reachable.
