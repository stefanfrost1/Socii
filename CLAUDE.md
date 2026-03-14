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
│       │   ├── company.py           # Company, CompanyTag
│       │   ├── interaction.py       # Interaction, InteractionAISummary
│       │   ├── project.py           # Project, ProjectStage, ProjectContact, ProjectCompany, ProjectTag
│       │   ├── reminder.py          # Reminder
│       │   └── tag.py               # Tag
│       ├── routers/
│       │   ├── auth.py              # Domain-restricted registration via Supabase invite
│       │   ├── contacts.py          # CRUD + timeline + merge + image import
│       │   ├── companies.py
│       │   ├── projects.py
│       │   ├── interactions.py      # Creates Celery task on save; action-point toggle; reprocess
│       │   ├── stages.py            # Pipeline stage management + reorder
│       │   ├── tags.py
│       │   ├── reminders.py
│       │   ├── search.py            # Full-text search across contacts & companies
│       │   └── dashboard.py         # Overview: recent interactions, pipeline, reminders
│       ├── services/
│       │   ├── ai.py                # Claude API: summarise_interaction, score_merge_candidates
│       │   ├── image_search.py      # og:image scraping from social URLs for contact photos
│       │   └── storage.py           # Supabase Storage helpers (resize → WebP → upload)
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
        ├── middleware.ts            # Route protection + session cookie refresh
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
        │   └── ui/
        │       ├── nav.tsx          # Sidebar navigation component
        │       └── session-refresher.tsx  # Activity-based JWT refresh (every 30 min)
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
| Image processing | Pillow | 10.4.0 |
| HTML parsing | beautifulsoup4 | 4.12.3 |
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
| Date utilities | date-fns | 4.x |

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

# Domain-based signup restriction (only @this-domain emails can register)
ALLOWED_EMAIL_DOMAIN=simplitics.se

# Comma-separated list of allowed CORS origins (add production URL here)
CORS_ORIGINS=http://localhost:3000

# Frontend — available client-side
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://[PROJECT].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon key>
NEXT_PUBLIC_ALLOWED_EMAIL_DOMAIN=simplitics.se
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
- Celery worker: internal
- Redis: internal

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

1. Users register via `POST /api/v1/auth/register` — restricted to `ALLOWED_EMAIL_DOMAIN`. The backend sends a Supabase invite email via the Admin API.
2. Users complete sign-in via **Supabase Auth** in the frontend (login/register pages).
3. The frontend retrieves a JWT access token via `getToken()` in `src/lib/supabase.ts`.
4. All API calls include `Authorization: Bearer <token>` (see `src/lib/api.ts`).
5. The backend validates the JWT in `app/auth.py` using `python-jose` with `SUPABASE_KEY` as the HS256 secret.
6. Every protected route depends on `get_current_user` (FastAPI `Depends`).
7. `src/middleware.ts` enforces route protection server-side: unauthenticated users are redirected to `/login`; authenticated users accessing `/login` or `/register` are redirected to `/`.
8. `SessionRefresher` (mounted in the root layout) proactively refreshes the Supabase JWT on user activity at most once every 30 minutes, resetting the session expiry window.

### AI Integration

- **Interaction summarisation**: when a new interaction is saved (or updated), the router immediately enqueues a `process_interaction_ai` Celery task on the `interactions_ai` queue.
- The task calls `summarise_interaction()` in `app/services/ai.py`, which calls `claude-haiku-4-5-20251001`.
- Input is truncated to 6 000 characters. The response must be strict JSON: `summary`, `action_points` (with `text`, `due_date`, `priority`), `follow_up_date`, `key_topics`, `sentiment`.
- The result is upserted into `interaction_ai_summaries`. Action points with due dates automatically create `Reminder` records linked to the interaction and contact.
- The frontend polls `GET /api/v1/interactions/{id}/ai-summary` — returns HTTP 202 while `pending`/`processing`, HTTP 200 when `done` or `failed`.
- Individual action points can be toggled complete via `PATCH /api/v1/interactions/{id}/action-points/{index}`.
- Re-processing can be triggered via `POST /api/v1/interactions/{id}/reprocess`.
- **Merge detection**: `scan_merge_candidates` (queue `merge_scan`) compares all non-archived contacts. Exact email match → 1.0 confidence; name similarity ≥ 0.85 → 0.75 confidence. Pairs above 0.4 create `contact_merge_suggestions` records, skipping already-pending pairs.

### Image Handling

- Contact avatars and company logos are stored in the Supabase Storage bucket **`socii-media`**.
- All images are resized to a maximum of 500×500 and converted to **WebP** (quality 85) before upload.
- Storage paths: `contacts/{id}/avatar.webp`, `companies/{id}/logo.webp`.
- Image candidates can be auto-discovered by scraping `og:image` tags from a contact's social URLs (LinkedIn, Twitter, GitHub, Instagram, website).
- Relevant endpoints:
  - `POST /contacts/{id}/image` — upload a file
  - `DELETE /contacts/{id}/image` — remove stored image
  - `POST /contacts/{id}/image/search` — discover URL candidates
  - `POST /contacts/{id}/image/import` — import from a URL

### Database

- PostgreSQL hosted on Supabase.
- All models use UUID primary keys (generated via `uuid.uuid4()`).
- `contacts` and `companies` have `tsvector` generated columns (`fts`) with GIN indexes for full-text search — defined in the migration, not the SQLModel classes.
- All major entities have `is_archived` soft-delete flags. **`DELETE /contacts/{id}` sets `is_archived=True` — it does not hard-delete.**
- Migrations live in `backend/alembic/versions/`. Always use Alembic — never modify the schema manually.

### API Conventions

- All routes are prefixed `/api/v1`.
- Health check: `GET /health` (unauthenticated).
- Routers are in `backend/app/routers/`. Each file corresponds to one resource.
- **Route ordering matters**: in `contacts.py`, all specific paths (`/needs-contact`, `/merge-suggestions`, `/check-duplicate`, `/merge`, etc.) must be declared **before** the `/{contact_id}` catch-all. Follow this pattern in any router that mixes specific and parameterised paths.
- CORS origins are configured via the `CORS_ORIGINS` environment variable (comma-separated). Update this for production — do not hardcode origins in `main.py`.
- `PUT` and `PATCH` on contacts delegate to the same handler and both accept a partial dict.

### Frontend Conventions

- **App Router** with a `(app)` route group that wraps all authenticated pages. Auth is enforced in both `src/middleware.ts` (server-side redirect) and the group layout.
- `src/lib/api.ts` is the single source of truth for all backend calls — add new endpoints here as typed functions.
- `src/lib/types.ts` mirrors backend models as TypeScript interfaces — keep in sync when models change.
- Styling: **Tailwind CSS** utility classes; `cn()` from `src/lib/utils.ts` for conditional class merging.
- Data fetching: **SWR** for cached/reactive fetches; direct `await api.*()` calls for mutations.

### Celery Queues

| Queue | Task | Purpose |
|-------|------|---------|
| `interactions_ai` | `process_interaction_ai` | Claude AI summarisation of interaction notes |
| `merge_scan` | `scan_merge_candidates` | Duplicate contact detection |

Both queues must be specified when starting the worker. Tasks auto-retry on any exception with exponential backoff (max 3 retries, ceiling 900 s).

## Data Models (Key Fields)

### Contact
`id`, `first_name`, `last_name`, `display_name`, `email` (unique), `email_secondary`, `phone`, `phone_secondary`, `title`, `image_url`, `image_storage_path`, `linkedin_url`, `twitter_url`, `github_url`, `instagram_url`, `website_url`, `address_city`, `address_country`, `birthday`, `bio_notes`, `last_contacted_at`, `contact_frequency_days`, `is_archived`

Join tables: `contact_companies` (with `role`, `is_primary`, `started_at`, `ended_at`), `contact_tags`

### Company
`id`, `name`, `website_url`, `linkedin_url`, `industry`, `size_range`, `description`, `logo_url`, `logo_storage_path`, `address_city`, `address_country`, `is_archived`

Join table: `company_tags`

### Project
`id`, `name`, `description`, `stage_id`, `stage_updated_at`, `value_estimate`, `currency`, `close_date_target`, `close_date_actual`, `outcome`, `is_archived`

Join tables: `project_contacts` (with `role`), `project_companies`, `project_tags`

### ProjectStage
`id`, `name`, `order_index`, `color` (hex), `is_terminal`, `is_default`

### Interaction
`id`, `contact_id`, `project_id`, `raw_content`, `interaction_type`, `interaction_date`, `direction`, `from_whom`, `ai_status` (`pending` | `processing` | `done` | `failed`)

### InteractionAISummary
`id`, `interaction_id`, `summary`, `action_points` (JSON string), `follow_up_date`, `key_topics` (JSON string), `sentiment`, `model_used`, `prompt_version`, `processed_at`, `raw_response`

### Reminder
`id`, `contact_id`, `project_id`, `interaction_id`, `text`, `due_date`, `is_completed`, `completed_at`

### Tag
`id`, `name` (unique), `color` (hex)

### MergeSuggestion
`id`, `contact_a_id`, `contact_b_id`, `confidence_score`, `reasons` (JSON string), `status` (`pending` | `accepted` | `rejected`), `resolved_at`

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
| Add a new page | Add route under `frontend/src/app/(app)/` — auth is inherited from `middleware.ts` and the group layout |
| Modify DB schema | Create an Alembic migration; update the SQLModel class and `types.ts` in sync |
| Add an AI feature | Implement in `app/services/ai.py`; expose via a Celery task if async |
| Add router endpoints | Declare specific paths **before** parameterised `/{id}` paths in the same router |
| Commit work | Use descriptive imperative-mood messages; keep commits atomic |
| Push changes | `git push -u origin <branch>` to the designated branch |
| Open a PR | Target `main`; summarise changes and include a test plan |

## Updating This File

Keep CLAUDE.md current as the project evolves:

- Update the directory tree when new top-level files or directories are added.
- Document new commands (build, test, lint) as tooling is added.
- Record architecture decisions and key conventions as patterns emerge.
- Update the environment variables section when new variables are required.
- Keep the Data Models section in sync with `backend/app/models/` and `frontend/src/lib/types.ts`.
