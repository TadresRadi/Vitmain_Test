Vitmain
AI-powered marketing assistant for small businesses. Generates social media posts and matching images from a short brand onboarding questionnaire, with subscription tiers, Vodafone Cash payments, and an admin dashboard.

Tech Stack
Backend: Django 4.2 · DRF · SimpleJWT · PostgreSQL 15 · Redis 7 · Gunicorn
Frontend: React 18 · TypeScript · Vite · Tailwind · shadcn/ui · Zustand · TanStack Query · i18next (en/ar)
AI: Groq (text) · Pollinations / Replicate / Stability AI / DeepAI (images)
Auth: JWT + Google OAuth (allauth)
Payments: Vodafone Cash webhook
Infra: Docker Compose · Prometheus · Grafana · Sentry
CI/CD: GitHub Actions (lint, security, test, build, package)
Prerequisites
Docker 24+ and Docker Compose v2+
Git
(Optional, for local dev without Docker) Python 3.12, Node 20, PostgreSQL 15, Redis 7
Quick Start (Docker)
Clone
git clone https://github.com/TadresRadi/Vitmain_Test.gitcd Vitmain_Test
Create .env at repo root with all required variables. See DEPLOYMENT_GUIDE.md for the full list. Minimum to boot:
env

SECRET_KEY=<generate_a_50+_char_random_string>
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=vitmain_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://redis:6379/1
CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1

# Required only when DEBUG=false
VODAFONE_WEBHOOK_SECRET_TOKEN=<random>
VODAFONE_RECEIVER_NUMBER=<your_vodafone_number>

# Optional — AI features will degrade gracefully if missing
GROQ_API_KEY=
# Optional — Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Optional — error tracking
SENTRY_DSN=
Build and run
bash

docker-compose up --build
Run migrations (in a new terminal)
bash

docker-compose exec backend python manage.py migrate
Create a superuser (optional, for Django admin)
bash

docker-compose exec backend python manage.py createsuperuser
Access
Frontend: http://localhost
Backend API: http://localhost:8000/api/
Health check: http://localhost:8000/health/
Django admin: http://localhost:8000/admin/
Local Development (without Docker)
Backend
bash

cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
Frontend
bash

cd frontend
npm install
npm run dev    # http://localhost:5173
Set VITE_API_URL=http://localhost:8000/api in frontend/.env.

Testing
Backend (pytest)
bash

cd backend
pytest                         # run all
pytest --cov=. --cov-report=html    # with coverage
open htmlcov/index.html
Frontend (vitest)
bash

cd frontend
npm test                       # run all
npm run test:coverage          # with coverage
Linting & Type Checking
bash

# Backend
cd backend && flake8 .

# Frontend
cd frontend && npm run lint
cd frontend && npm run typecheck
Security Scanning
bash

cd backend
bandit -r . -n 5 -c bandit.yaml
pip-audit -r requirements.txt
bash

cd frontend
npm audit --audit-level=high
Project Structure
text

Vitmain_Test/
├── backend/                # Django 4.2
│   ├── backend/            # Project settings (wsgi, asgi, urls)
│   ├── core/               # Cross-cutting: auth, rate limit, audit, API keys
│   ├── users/              # Custom user, JWT, Google OAuth, admin
│   ├── chat/               # AI chat + image generation
│   ├── onboarding/         # Brand questionnaire
│   ├── subscriptions/      # Plan tiers + access control
│   ├── payments/           # Vodafone Cash webhook + matching
│   ├── support/            # User-to-admin support chat
│   ├── portfolio/          # Admin-curated landing content
│   └── monitoring/         # Prometheus + Grafana + Alertmanager config
├── frontend/               # React 18 + Vite
│   └── src/
│       ├── pages/          # Route components
│       ├── components/     # Reusable UI (incl. admin/, landing/, ui/)
│       ├── services/       # API wrappers (axios)
│       ├── store/          # Zustand stores
│       ├── hooks/          # Custom hooks + TanStack Query
│       └── lib/            # Axios instance, token storage, CSRF
├── docs/                   # Security checklist
├── .github/workflows/      # CI, CD, release workflows
├── docker-compose.yml      # Dev stack (db + redis + backend + frontend)
└── docker-compose.monitor.yml  # Optional: Prometheus + Grafana + Alertmanager
Documentation
DEPLOYMENT_GUIDE.md — Production deployment guide
docs/security.md — Security checklist and configuration
backend/monitoring/README_MONITORING.md — Observability stack setup
License
Apache License 2.0. See LICENSE for the full text.

Contributing
This project is under active hardening. See HARDENING_PLAN.md for the current remediation roadmap.

text


### Step 2 — Verify

Run these three commands and paste the output:

```bash
cd /home/z/my-project/repo/Vitmain_Test
wc -l README.md
head -5 README.md
Expected:

wc -l → ~150–170 lines
head -5 → starts with # Vitmain then a blank line then the description
Step 3 — Commit
bash

git add README.md
git commit -m "docs: add README with quickstart, structure, and dev guide

Resolves B5 from the production-readiness audit."
