# CLAUDE.md

This file provides guidance for AI assistants (Claude and others) working in this repository.

## Project Overview

**Socii** is a personal CRM (Customer Relationship Management) application. It lets users track contacts, companies, projects, and interactions, with AI-powered interaction summarisation via Claude and automated contact-merge detection.

- **Repository**: stefanfrost1/Socii
- **Default branch**: `main`

## Repository Structure

```
/
├── CLAUDE.md                        # This file
├── README.md                        # Project title placeholder
├── .env.example                     # Required environment variables
├── docker-compose.yml               # Full-stack local dev orchestration
│
├── backend/                         # Python / FastAPI service
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_schema.py   # Full DB schema + seed data
│   └── app/
│       ├── main.py                  # FastAPI app, CORS, router registration
│       ├── config.py                # Settings via pydantic-settings (.env)
│       ├── auth.py                  # Supabase JWT validation middleware
│       ├── database.py              # SQLModel engine / session
│       ├── worker.py                # Celery app definition
│       ├── models/
│       │   ├── contact.py           # Contact, ContactCompany, ContactTag, MergeSuggestion
│       │   ├── company.py
│       │   ├── interaction.py       # Interaction, InteractionAISummary
│       │   ├── project.py           # Project, ProjectStage, join tables
│       │   ├── reminder.py
│       │   └── tag.py
│       ├── routers/
│       │   ├── contacts.py          # CRUD + timeline + merge + image import
│       │   ├── companies.py
│       │   ├── projects.py
│       │   ├── interactions.py      # Creates Celery task on save
│       │   ├── stages.py            # Pipeline stage management + reorder
│       │   ├── tags.py
│       │   ├── reminders.py
│       │   ├── search.py            # Full-text search across contacts & companies
│       │   └── dashboard.py         # Overview: recent interactions, pipeline, reminders
│       ├── services/
│       │   ├── ai.py                # Claude API: summarise_interaction, score_merge_candidates
│       │   ├── image_search.py      # Web image search for contact photos
│       │   └── storage.py           # Supabase Storage helpers
│       └── tasks/
│           └── ai_tasks.py          # Celery tasks: process_interaction_ai, scan_merge_candidates
│
└── frontend/                        # Next.js 14 (App Router) TypeScript application
    ├── Dockerfile
    ├── .nvmrc
    ├── next.config.js
    ├── package.json
    ├── tailwind.config.ts
    └── src/
        ├── app/
        │   ├── layout.tsx           # Root layout
        │   ├── globals.css
        │   ├── login/page.tsx
        │   ├── register/page.tsx
        │   └── (app)/               # Authenticated route group
        │       ├── layout.tsx       # Nav + auth guard
        │       ├── page.tsx         # Dashboard
        │       ├── contacts/        # List, detail [id], new, merge
        │       ├── companies/
        │       ├── projects/        # List, new
        │       ├── interactions/    # Detail [id], new
        │       ├── reminders/
        │       ├── search/
        │       └── settings/
        │           ├── stages/      # Drag-and-drop pipeline editor
        │           └── tags/
        ├── components/
        │   └── ui/nav.tsx           # Sidebar navigation component
        └── lib/
            ├── api.ts               # Typed fetch wrappers for all backend endpoints
            ├── supabase.ts          # Supabase browser client + getToken()
            ├── types.ts             # Shared TypeScript interfaces
            └── utils.ts             # cn() helper (clsx + tailwind-merge)
```

## Technology Stack

### Backend

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.x |
| Framework | FastAPI | 0.115.0 |
| ORM | SQLModel (SQLAlchemy + Pydantic) | 0.0.21 |
| Database | PostgreSQL (via Supabase) | — |
| Migrations | Alembic | 1.13.3 |
| Auth | Supabase JWT (python-jose HS256) | — |
| Async tasks | Celery | 5.4.0 |
| Message broker | Redis | 5.1.1 |
| AI | Anthropic Python SDK | 0.36.2 |
| HTTP client | httpx | 0.27.2 |
| Server | uvicorn | 0.30.6 |

### Frontend

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | Next.js (App Router) | 14.2.15 |
| Language | TypeScript | 5.x |
| Auth | @supabase/auth-helpers-nextjs | 0.10.x |
| Styling | Tailwind CSS | 3.x |
| UI primitives | Radix UI | various |
| Data fetching | SWR | 2.x |
| Drag and drop | @dnd-kit | 6/8.x |
| Icons | lucide-react | 0.454.x |

## Environment Variables

Copy `.env.example` to `.env` and fill in real values before running.

```
# Supabase (database + auth + storage)
SUPABASE_DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT].supabase.co
SUPABASE_KEY=<service-role key>      # used for JWT validation and storage

# Anthropic (AI summaries)
ANTHROPIC_API_KEY=sk-ant-...

# Redis (broker + result backend for Celery)
REDIS_URL=redis://redis:6379/0

# Frontend — available client-side (also needed in .env for docker-compose)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://[PROJECT].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon key>
```

> **Never commit `.env` or any real credentials.**

## Running Locally

### With Docker Compose (recommended)

```bash
cp .env.example .env   # fill in values
docker compose up --build
```

Services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Redis: internal only

### Without Docker

**Backend**
```bash
cd backend
pip install -r requirements.txt
# Run migrations
alembic upgrade head
# Start API
uvicorn app.main:app --reload --port 8000
# Start Celery worker (separate terminal)
celery -A app.worker worker --loglevel=info -Q interactions_ai,merge_scan
```

**Frontend**
```bash
cd frontend
nvm use          # uses version in .nvmrc
npm install
npm run dev      # http://localhost:3000
```

## Key Commands

| Task | Command |
|------|---------|
| Start all services | `docker compose up --build` |
| Run DB migrations | `cd backend && alembic upgrade head` |
| Create new migration | `cd backend && alembic revision --autogenerate -m "description"` |
| Start API (dev) | `cd backend && uvicorn app.main:app --reload` |
| Start Celery worker | `cd backend && celery -A app.worker worker --loglevel=info -Q interactions_ai,merge_scan` |
| Frontend dev server | `cd frontend && npm run dev` |
| Frontend build | `cd frontend && npm run build` |
| Frontend lint | `cd frontend && npm run lint` |

## Architecture & Key Conventions

### Authentication Flow

1. Users authenticate via **Supabase Auth** in the frontend (login/register pages).
2. The frontend retrieves a JWT access token via `getToken()` in `src/lib/supabase.ts`.
3. All API calls include `Authorization: Bearer <token>` (see `src/lib/api.ts`).
4. The backend validates the JWT in `app/auth.py` using `python-jose` with `SUPABASE_KEY` as the HS256 secret.
5. Every protected route depends on `get_current_user` (FastAPI `Depends`).

### AI Integration

- **Interaction summarisation**: when a new interaction is saved, the router immediately enqueues a `process_interaction_ai` Celery task on the `interactions_ai` queue.
- The task calls `summarise_interaction()` in `app/services/ai.py`, which calls `claude-haiku-4-5-20251001`.
- The response is parsed and stored in `interaction_ai_summaries`. Action points with due dates automatically create `Reminder` records.
- The frontend polls `GET /api/v1/interactions/{id}/ai-summary` until `ai_status == "done"`.
- **Merge detection**: `scan_merge_candidates` (queue `merge_scan`) compares all non-archived contacts using email equality and name similarity (SequenceMatcher). Pairs above 0.4 confidence score create `contact_merge_suggestions` records.

### Database

- PostgreSQL hosted on Supabase.
- All models use UUID primary keys.
- `contacts` and `companies` have `tsvector` generated columns (`fts`) with GIN indexes for full-text search.
- All major entities have `is_archived` soft-delete flags.
- Migrations live in `backend/alembic/versions/`. Always use Alembic — never modify the schema manually.

### API Conventions

- All routes are prefixed `/api/v1`.
- Health check: `GET /health` (unauthenticated).
- Routers are in `backend/app/routers/`. Each file corresponds to one resource.
- CORS is currently configured to allow only `http://localhost:3000` — update `main.py` for production domains.

### Frontend Conventions

- **App Router** with a `(app)` route group that wraps all authenticated pages.
- `src/lib/api.ts` is the single source of truth for all backend calls — add new endpoints here as typed functions.
- `src/lib/types.ts` mirrors backend models as TypeScript interfaces — keep in sync when models change.
- Styling: **Tailwind CSS** utility classes; `cn()` from `src/lib/utils.ts` for conditional class merging.
- Data fetching: **SWR** for cached/reactive fetches; direct `await api.*()` calls for mutations.

### Celery Queues

| Queue | Task | Purpose |
|-------|------|---------|
| `interactions_ai` | `process_interaction_ai` | Claude AI summarisation of interaction notes |
| `merge_scan` | `scan_merge_candidates` | Duplicate contact detection |

Both queues must be specified when starting the worker (see commands above).

## Testing

No automated test suite exists yet. When tests are added, document:

- How to run the full suite
- How to run a single test
- Required environment setup (test DB, mocked Anthropic client, etc.)

## Git Workflow

### Branch Naming

- Claude agent branches: `claude/<short-description>-<session-id>`
- Human feature branches: `feat/<short-description>`
- Bug fixes: `fix/<short-description>`

### Development Flow

1. Always develop on the designated branch — never push directly to `main`.
2. Create the branch locally if it does not exist, then push with tracking:
   ```bash
   git checkout -b <branch-name>
   git push -u origin <branch-name>
   ```
3. Write clear, descriptive commit messages in the imperative mood (e.g., `Add contact merge UI`).
4. Open a pull request targeting `main` when work is complete.

### Push Instructions

```bash
git push -u origin <branch-name>
```

- Retry on network failure with exponential backoff: 2 s → 4 s → 8 s → 16 s.
- Never force-push to `main`.

## Common Tasks for AI Assistants

| Task | Notes |
|------|-------|
| Explore codebase | Read `backend/app/main.py`, `backend/app/models/`, `frontend/src/lib/types.ts` first |
| Add a new resource | Create model → router → register in `main.py` → add API functions to `api.ts` → add types to `types.ts` |
| Add a new page | Add route under `frontend/src/app/(app)/` — auth is inherited from the group layout |
| Modify DB schema | Create an Alembic migration; update the SQLModel class and `types.ts` in sync |
| Add an AI feature | Implement in `app/services/ai.py`; expose via a Celery task if async |
| Commit work | Use descriptive imperative-mood messages; keep commits atomic |
| Push changes | `git push -u origin <branch>` to the designated branch |
| Open a PR | Target `main`; summarise changes and include a test plan |

## Updating This File

Keep CLAUDE.md current as the project evolves:

- Update the directory tree when new top-level files or directories are added.
- Document new commands (build, test, lint) as tooling is added.
- Record architecture decisions and key conventions as patterns emerge.
- Update the environment variables section when new variables are required.
