# MathEd Romania — Development Setup Guide

## Prerequisites

You should already have installed:
- Python 3.12+
- Node.js 20+ / npm 10+
- PostgreSQL 16+ (with psql in PATH)
- Docker & Docker Compose
- Git

## Step-by-Step Setup

### 1. Clone & Enter the Project

```bash
cd mathed-romania
```

### 2. Environment Variables

```bash
cp .env.example .env
```

The defaults match docker-compose.yml, so no editing needed for local dev.

### 3. Start PostgreSQL + Redis

```bash
docker compose up -d
```

Verify they're running:
```bash
docker compose ps
# Should show mathed_postgres and mathed_redis both "Up"
```

You can also connect via pgAdmin 4:
- Host: localhost
- Port: 5432
- Database: mathed_romania
- User: mathed_user
- Password: mathed_local_pass

### 4. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (this creates all tables including the custom User model)
python manage.py migrate

# Create your admin account
python manage.py createsuperuser
# Use your email (not username — we removed the username field)

# Start the development server
python manage.py runserver
```

Verify: Open http://localhost:8000/admin/ and log in with your superuser credentials.

### 5. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Verify: Open http://localhost:5173 — you should see the MathEd Romania landing page.

The Vite dev server proxies `/api/*` requests to Django on port 8000, so both servers need to be running simultaneously during development.

### 6. Verify the Full Stack

1. Django admin is accessible at http://localhost:8000/admin/
2. You can see User, Grade, Unit, Lesson, Exercise, Test models in the admin
3. Frontend loads at http://localhost:5173
4. Debug Toolbar appears on Django pages (bottom-right corner)

## Daily Development Workflow

```bash
# Terminal 1: Databases (if not already running)
docker compose up -d

# Terminal 2: Backend
cd backend && source .venv/bin/activate
python manage.py runserver

# Terminal 3: Frontend
cd frontend && npm run dev
```

## Common Commands

```bash
# Backend
python manage.py makemigrations     # After model changes
python manage.py migrate            # Apply migrations
python manage.py createsuperuser    # Create admin user
python manage.py shell_plus         # Enhanced Django shell (django-extensions)

# Frontend
npm run dev                         # Start dev server
npm run build                       # Production build
npm run lint                        # Run ESLint

# Docker
docker compose up -d                # Start databases
docker compose down                 # Stop databases
docker compose logs -f db           # View PostgreSQL logs
```

## Project-Specific Notes

- **Custom User Model:** Email-based auth (no username). The `AUTH_USER_MODEL = "users.User"` setting is baked in from day one. Never change this after the first migration.
- **Settings Split:** `config/settings/base.py` (shared), `development.py` (local), `production.py` (Railway/VPS). `manage.py` defaults to development.
- **CORS:** The dev settings allow requests from `localhost:5173` (Vite). Production requires explicit domain configuration.
- **JWT Cookies:** Tokens are stored in httpOnly cookies (not localStorage) for security — important since our users are minors.
