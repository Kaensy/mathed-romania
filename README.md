# MathEd Romania

Educational math platform for Romanian middle schoolers (grades 5–8), following the official Romanian curriculum (OMEN nr. 3393/28.02.2017).

**Bachelor's Thesis Project** — See `docs/MathEd_Romania_Reference_v2.pdf` for the full project specification.

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | React 19 + TypeScript + Tailwind CSS |
| Backend    | Django 5.1 + Django REST Framework  |
| Database   | PostgreSQL 16 + Redis 7             |
| Math       | KaTeX                               |
| Auth       | Django Simple JWT (httpOnly cookies) |
| Desktop    | PWA (Progressive Web App)           |

## Project Structure

```
mathed-romania/
├── backend/                # Django project
│   ├── config/             # Settings (base/dev/prod), URLs, WSGI/ASGI
│   ├── apps/
│   │   ├── users/          # Custom User model, auth, profiles
│   │   ├── content/        # Grades, Units, Lessons, Exercises, Tests
│   │   └── progress/       # Tracking, attempts, streaks, classroom pacing
│   ├── manage.py
│   └── requirements.txt
├── frontend/               # React + Vite project
│   ├── src/
│   │   ├── api/            # Axios client with JWT refresh
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Route-level components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── types/          # TypeScript type definitions
│   │   └── utils/          # Helpers (math rendering, etc.)
│   └── package.json
├── docker-compose.yml      # PostgreSQL + Redis for local dev
├── .env.example
└── docs/
```

## Quick Start

See `docs/SETUP.md` for detailed instructions.

```bash
# 1. Start databases
docker compose up -d

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev
```

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000/api/v1/
- **Django Admin:** http://localhost:8000/admin/

## Development Phases

- [x] Phase 0: Foundation (project scaffolding)
- [ ] Phase 1: Core Authentication
- [ ] Phase 2: Content Management System
- [ ] Phase 3: First Lessons
- [ ] Phase 4: Exercise System
- [ ] Phase 5: Testing System
- [ ] Phase 6: Teacher Features
- [ ] Phase 7: MVP Polish
