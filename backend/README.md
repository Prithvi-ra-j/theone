# Dristhi Backend: Core API & AI Orchestration

This is the FastAPI-powered engine for the Dristhi platform, responsible for multilingual AI recommendations, site-wide context awareness, and core business logic.

---

## 🛠️ Tech Stack & Requirements
- **Runtime:** Python 3.13.2+
- **Framework:** FastAPI
- **Database:** SQLite (Local) / PostgreSQL (managed via Render)
- **AI:** LangChain + Multi-Agent Architecture
- **Cache:** Redis (for session management and background tasks)

---

## 🚀 Local Development

### 1. Setup Virtual Environment
```bash
python -m venv .venv
# Activate:
# Windows: .\.venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file based on `env.example`. Ensure you set:
- `API_LLM_API_KEY`: Your OpenRouter or LLM provider key.
- `SECRET_KEY`: A secure string for JWT tokens.

### 4. Database Migrations
We use Alembic for schema management:
```bash
alembic upgrade head
```

### 5. Run the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🏗️ Architecture Note
The backend uses a **Multi-Agent** approach. Requests are routed via the `AIService` to specialized agents (**Career**, **Finance**, **Wellness**) based on user intent. It also integrates a `ContextService` that feeds site-wide user data into the AI prompts for "conscious" responses.

---

## 📡 Essential Endpoints
- **Swagger UI:** `/docs`
- **Health Check:** `/health`
- **AI Assist:** `/api/v1/mini-assistant/stream` (Streaming support)

---

## ⚖️ License
MIT
