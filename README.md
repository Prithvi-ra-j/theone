# Dristhi

AI-powered career & life improvement platform focused on helping students build skills, manage habits, track finances, and improve wellbeing.

This README is a concise, actionable developer-first guide to run and contribute to the project locally.

---

## Quick overview
- Frontend: React + Vite + Tailwind
- Backend: FastAPI (Python)
- DB: PostgreSQL
- Cache: Redis
- AI: Ollama (local LLMs) + LangChain integrations
- Orchestration: Docker Compose

---

## Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.11+
- Docker & Docker Compose (v2+)
- Git

---

## Quickstart (Docker)
1. Copy env files

```powershell
cp backend/env.example backend/.env
cp frontend/.env.example frontend/.env
```

2. Start services

```powershell
# From repo root
docker-compose -f infra/docker-compose.yml up --build -d
```

3. Visit
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

---

## Development (local, without Docker)

### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate    # Windows PowerShell
pip install -r requirements.txt
# configure backend/.env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```powershell
cd frontend
npm install
# create frontend/.env (see frontend/.env.example)
npm run dev
```

---

## Environment variables
- Backend: `backend/.env` (copy from `backend/env.example`). Key entries:
  - DATABASE_URL
  - REDIS_URL
  - SECRET_KEY
  - JWT_ALGORITHM
  - ACCESS_TOKEN_EXPIRE_MINUTES
- Frontend: `frontend/.env` (copy from `frontend/.env.example`). Key entries:
  - VITE_API_BASE_URL (e.g. http://localhost:8000)
  - VITE_APP_NAME

---

## Useful commands (Makefile)
- `make setup` — initial setup (build images, create volumes)
- `make dev` — run services in development
- `make dev-backend`, `make dev-frontend` — run single services
- `make migrate` — run DB migrations
- `make seed` — seed sample data
- `make db-reset` — reset DB

---

## API endpoint checklist
If you want to validate endpoints quickly, there is a helper script:

```powershell
python .\tools\check_endpoints.py --verbose --force-get
```

It reads frontend `src/api/config.js` and tests each declared path against the backend base (default http://localhost:8000/api/v1). Use `--base` to override, `--token` to test auth-protected endpoints.

---

## Contributing
- Fork → feature branch → PR
- Write tests and follow linters
- Backend: Black / isort / flake8 / mypy
- Frontend: ESLint / Prettier

---

## Troubleshooting
- If frontend cannot reach backend, ensure `VITE_API_BASE_URL` points to the running backend and that CORS is enabled in FastAPI.
- If Docker containers fail, check ports (8000/3000/5432/6379) or run `docker-compose ps` and `docker-compose logs`.

---

## License
MIT

---

If you'd like, I can also:
- Add a short `DEVELOPMENT.md` with step-by-step common tasks (run tests, add migrations, run frontend tests)
- Add CI workflow templates for GitHub Actions that run linting and tests🎯 Dristhi - AI-Powered Career & Life Improvement Platform
Empowering Indian students with personalized AI-driven career guidance, habit tracking, financial wisdom, and life optimization.

License: MIT
Python 3.11+
React 18
FastAPI
Docker

🌟 Overview
Dristhi is a comprehensive, open-source platform designed specifically for Indian students to achieve their career and life goals. It combines AI-powered insights with practical tools for habit formation, financial management, mood tracking, and personalized learning paths.

✨ Key Features
🤖 AI-Powered Career Guidance - Personalized advice using Ollama + LangChain
📊 Smart Habit Tracking - Gamified habit formation with streak analytics
💰 Financial Wisdom - Budget management, investment advice, and financial planning
🧠 Mood & Wellness - Comprehensive mental health tracking and insights
🏆 Gamification System - Badges, achievements, and progress rewards
🧠 Memory & Personalization - FAISS-powered user memory and AI insights
📱 Modern Web App - Responsive React frontend with beautiful UI
🔒 Enterprise Security - JWT authentication, rate limiting, and data encryption
🏗️ Architecture
```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │ Infrastructure  │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Docker)      │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • REST APIs     │    │ • PostgreSQL    │
│ • Career Tools  │    │ • AI Services   │    │ • Redis         │
│ • Habit Tracker │    │ • Auth System   │    │ • Ollama        │
│ • Finance Mgmt  │    │ • Memory Store  │    │ • Monitoring    │
│ • Mood Tracking │    │ • Background    │    │ • CI/CD         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```
🚀 Quick Start
Prerequisites
Docker & Docker Compose (v2.0+)
Node.js (v18.0+)
Python (v3.11+)
Git
1. Clone the Repository
bash
git clone https://github.com/yourusername/dristhi.git
cd dristhi
2. Environment Setup
bash
# Copy environment files
cp backend/env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend environment variables
nano backend/.env
Required Environment Variables:

bash
# Backend (.env)
DATABASE_URL=postgresql://postgres:password@localhost:5432/dristhi
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Frontend (.env)
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Dristhi
3. Start All Services
bash
# Using Makefile (recommended)
make setup          # First time setup
make dev            # Start all services

# Or manually with Docker Compose
docker-compose -f infra/docker-compose.yml up -d
4. Access the Application
Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs
Grafana: http://localhost:3001 (admin/admin)
Prometheus: http://localhost:9090
🛠️ Development Setup
Backend Development
bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Frontend Development
bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
Database Management
bash
# Reset database
make db-reset

# Run migrations
make migrate

# Seed sample data
make seed

# View logs
make logs
📁 Project Structure
text
dristhi/
├── 📁 backend/                 # FastAPI Backend
│   ├── 📁 app/
│   │   ├── 📁 core/           # Configuration & settings
│   │   ├── 📁 models/         # Database models
│   │   ├── 📁 schemas/        # Pydantic schemas
│   │   ├── 📁 routers/        # API endpoints
│   │   ├── 📁 services/       # Business logic
│   │   ├── 📁 utils/          # Helper functions
│   │   └── 📁 tasks/          # Background jobs
│   ├── 📁 alembic/            # Database migrations
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile             # Backend container
├── 📁 frontend/               # React Frontend
│   ├── 📁 src/
│   │   ├── 📁 components/     # Reusable UI components
│   │   ├── 📁 pages/          # Application pages
│   │   ├── 📁 api/            # API integration
│   │   ├── 📁 hooks/          # React Query hooks
│   │   └── 📁 utils/          # Utility functions
│   ├── package.json           # Node.js dependencies
│   └── Dockerfile             # Frontend container
├── 📁 infra/                  # Infrastructure
│   ├── docker-compose.yml     # Service orchestration
│   ├── prometheus.yml         # Monitoring config
│   └── 📁 grafana/            # Dashboard definitions
├── Makefile                   # Development commands
├── README.md                  # This file
└── PROJECT_STATUS.md          # Project progress
🔧 Available Commands
Development Commands
bash
make dev              # Start all services
make dev-backend      # Start only backend
make dev-frontend     # Start only frontend
make build            # Build all containers
make start            # Start production containers
make stop             # Stop all services
Database Commands
bash
make migrate          # Run database migrations
make seed             # Seed sample data
make db-reset         # Reset database
make db-backup        # Backup database
Testing Commands
bash
make test             # Run all tests
make test-backend     # Backend tests only
make test-frontend    # Frontend tests only
make lint             # Code linting
Utility Commands
bash
make logs             # View service logs
make health           # Check service health
make clean            # Clean up containers
make setup            # Initial setup
🐛 Troubleshooting Guide
Common Issues & Solutions
1. Docker Services Won't Start
Problem: Services fail to start or show connection errors

bash
# Check Docker status
docker --version
docker-compose --version

# Restart Docker Desktop
# Clear Docker cache
docker system prune -a

# Check port conflicts
netstat -an | grep :8000
netstat -an | grep :3000
Solution:

Ensure Docker Desktop is running
Check if ports 8000, 3000, 5432, 6379 are available
Restart Docker services
2. Database Connection Issues
Problem: Backend can't connect to PostgreSQL

bash
# Check database status
docker-compose -f infra/docker-compose.yml ps postgres

# View database logs
docker-compose -f infra/docker-compose.yml logs postgres

# Test connection
docker exec -it dristhi-postgres-1 psql -U postgres -d dristhi
Solution:

Wait for PostgreSQL to fully initialize (first startup takes time)
Check environment variables in backend/.env
Verify database credentials
3. Frontend Build Failures
Problem: React app fails to build or start

bash
# Clear node modules
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 18.0+

# Clear npm cache
npm cache clean --force
Solution:

Use Node.js 18+ (LTS version recommended)
Clear npm cache and reinstall dependencies
Check for syntax errors in React components
4. AI Services Not Working
Problem: Ollama AI responses fail or timeout

bash
# Check Ollama service
docker-compose -f infra/docker-compose.yml ps ollama

# Test Ollama connection
curl http://localhost:11434/api/tags

# Check model availability
docker exec -it dristhi-ollama-1 ollama list
Solution:

Ensure Ollama service is running
Download required models: docker exec -it dristhi-ollama-1 ollama pull llama2
Check Ollama logs for errors
5. Authentication Issues
Problem: Login fails or tokens expire quickly

bash
# Check JWT configuration
cat backend/.env | grep JWT

# Verify secret key length
# Should be at least 32 characters
Solution:

Generate a strong SECRET_KEY (32+ characters)
Check token expiration settings
Verify frontend API base URL
6. Performance Issues
Problem: Slow response times or high memory usage

bash
# Check resource usage
docker stats

# Monitor service health
make health

# Check logs for errors
make logs
Solution:

Increase Docker memory allocation
Check for memory leaks in services
Optimize database queries
Log Analysis
Backend Logs
bash
# View real-time backend logs
docker-compose -f infra/docker-compose.yml logs -f backend

# Check specific error types
docker-compose -f infra/docker-compose.yml logs backend | grep ERROR
Frontend Logs
bash
# Browser console errors
# Check Network tab for API failures
# Verify environment variables
Database Logs
bash
# PostgreSQL logs
docker-compose -f infra/docker-compose.yml logs postgres

# Redis logs
docker-compose -f infra/docker-compose.yml logs redis
Health Checks
bash
# Check all services
make health

# Individual service checks
curl http://localhost:8000/health
curl http://localhost:3000
curl http://localhost:5432
curl http://localhost:6379
🧪 Testing
Backend Testing
bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
Frontend Testing
bash
cd frontend
npm test
npm run test:coverage
Integration Testing
bash
# Start test environment
docker-compose -f infra/docker-compose.test.yml up -d

# Run integration tests
make test-integration

# Cleanup
docker-compose -f infra/docker-compose.test.yml down
📊 Monitoring & Observability
Metrics Dashboard
Grafana: http://localhost:3001 (admin/admin)
Prometheus: http://localhost:9090
Custom Dashboards: Pre-configured for Dristhi services
Key Metrics
API response times and error rates
Database performance and connections
AI service response times
User activity and engagement
System resource usage
Log Aggregation
Structured logging with Loguru
OpenTelemetry tracing
Centralized log collection
Error tracking and alerting
🚀 Deployment
Production Deployment
bash
# Build production images
make build-prod

# Deploy to production
make deploy-prod

# Scale services
docker-compose -f infra/docker-compose.prod.yml up -d --scale backend=3
Environment-Specific Configs
Development: docker-compose.yml
Staging: docker-compose.staging.yml
Production: docker-compose.prod.yml
CI/CD Pipeline
Automated testing on pull requests
Security scanning with Trivy
Docker image building and testing
Automated deployment to staging/production
🤝 Contributing
We welcome contributions! Please see our Contributing Guide for details.

Development Workflow
Fork the repository
Create a feature branch
Make your changes
Add tests
Submit a pull request
Code Standards
Backend: Black, isort, flake8, mypy
Frontend: ESLint, Prettier
Documentation: Clear docstrings and README updates
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
FastAPI team for the excellent web framework
React community for the frontend ecosystem
Ollama team for local LLM capabilities
LangChain for AI orchestration tools
Tailwind CSS for the beautiful UI components
📞 Support
Issues: GitHub Issues
Discussions: GitHub Discussions
Documentation: Wiki
Made with ❤️ for Indian students pursuing their dreams