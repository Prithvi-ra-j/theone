# Dristhi: AI-Powered Career & Life Optimization

**Dristhi** is a premium, state-of-the-art career and life improvement platform designed specifically for the modern Indian student. It leverages advanced AI orchestration, site-wide context awareness, and high-end design to help you reach your maximum potential.

---

## Recent Premium Upgrades

*   ** Site-Wide Contextual AI** The AI Assistant is now "conscious" of your entire platform progress. It aggregates data from your habit streaks, financial goals, and career milestones to provide hyper-personalized advice.
*   **🇮🇳 Hyper-Localization (Multilingual):** Official support for **English**, **Hindi**, and **Hinglish**. The AI Assistant adapts its tone and culturally relevant cues to match the Indian college experience.
*   ** State-of-the-Art UI/UX:** A complete frontend overhaul using **Premium Glassmorphism**. Experience a sleek, translucent, and blurred aesthetic with smooth micro-animations.
*   ** "Slide & Summarize" Memory:** A robust memory system that maintains long-term conversation context without hitting token limits, ensuring the AI never forgets your journey.
*   ** Python 3.13 Core:** Optimized for the latest Python release (3.13.2) with pinned dependencies for seamless deployment on Render.

---

##  Features at a Glance

*   ** Smart Career Advisor:** Personalized roadmaps, skill gap analysis, and "Reality Checks" for parallel career planning.
*   ** Financial Intelligence:** Budgeting, ROI analysis for education, and financial goal tracking.
*   ** Dynamic Habit Lab:** Gamified habit tracking with streak-based rewards and analytics.
*   ** Intelligence Dashboard:** Proactive "Nudge" system that identifies where you need focus today.

---

##  Technical Stack

*   **Frontend:** React 18 + Vite + Tailwind CSS (Glassmorphism Core)
*   **Backend:** FastAPI + Python 3.13.2
*   **AI Orchestration:** LangChain + Multi-Agent Architecture
*   **Memory Store:** SQLite (Local) / PostgreSQL (Production) + Redis
*   **Infrastructure:** Docker & Render Blueprint support

---

## 🚀 Quick Start

### 1. Prerequisites
- **Node.js 18+**
- **Python 3.13.2+**
- **Docker Compose** (Optional but recommended)

### 2. Environment Setup
Create a `.env` file in the `backend/` directory using `env.example` as a template:

```bash
# Important keys
SECRET_KEY=your_generated_secret
LLM_PROVIDER=api
API_LLM_API_KEY=your_openrouter_api_key
API_LLM_MODEL=google/gemini-2.0-flash-exp:free
```

### 3. Run Locally (Standard)

**Backend:**
```bash
cd backend
python -m venv .venv
# Activate venv
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 4. Deploy to Render
The project includes a `render.yaml` blueprint. Simply connect your GitHub repository to Render, and it will automatically:
- Detect **Python 3.13.2**.
- Provision **Postgres** and **Redis**.
- Run the build and start commands as configured.

---

## ⚖️ License
MIT License. Created with ❤️ for Indian students pursuing their dreams.
