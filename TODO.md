# Socii CRM — Improvement Backlog

Generated from a full codebase review. Items are ordered by priority within each tier.

---

## 🔴 Critical

> Security issues and real bugs that must be fixed before any production use.

- [ ] **No multi-tenancy / user isolation** — `get_current_user` extracts the JWT `sub` but it is never stored on any entity or used to scope queries. Every authenticated user can read and mutate every record in the database. Add `owner_id uuid NOT NULL` to all major tables, filter every query by `owner_id = current_user["sub"]`, and add a migration.

- [ ] **Mass assignment vulnerability on all update endpoints** — `PUT /contacts`, `PUT /companies`, `PUT /projects`, and `PUT /interactions` iterate over a raw `dict` body and call `setattr(model, k, v)` for any key that `hasattr()` finds. A client can overwrite `is_archived`, `image_storage_path`, `ai_status`, and any other field arbitrarily. Define typed `ContactUpdate`, `CompanyUpdate`, `ProjectUpdate`, and `InteractionUpdate` Pydantic models exposing only patchable fields.

- [ ] **Broken edit link on contact detail page** — `contacts/[id]/page.tsx:96` links to `/contacts/${id}/edit` but `contacts/[id]/edit/page.tsx` does not exist. Clicking Edit produces a 404.

- [ ] **AI re-triggered on any field update** — `PUT /interactions/{id}` always resets `ai_status = "pending"` and enqueues a new Celery task regardless of whether `raw_content` changed. Updating `interaction_type` or `from_whom` wastes Claude API credits. Only enqueue the task when `raw_content` has actually changed.

- [ ] **`to_tsquery` input not sanitised** — `search.py:18` constructs `ts_query = " & ".join(q.strip().split())` and passes it directly into `to_tsquery('english', :tsq)`. Inputs containing tsquery metacharacters (`|`, `&`, `!`, `(`, `)`, `:*`) cause PostgreSQL errors. Replace with `plainto_tsquery`, which accepts raw text without parsing issues.

- [ ] **No rate limiting** — `POST /auth/register` (triggers Supabase invite emails), `POST /contacts/{id}/image/search` (makes external HTTP requests), and `POST /contacts/merge-suggestions/scan` (O(n²) CPU task) can all be called in a tight loop. Add rate limiting middleware (e.g. `slowapi`).

- [ ] **Merge does not resolve the MergeSuggestion record** — `POST /contacts/merge` performs the merge but never updates the associated `MergeSuggestion` to `accepted`. After merging, the suggestion stays `pending` and reappears on the next page load. Resolve the suggestion inside the same database transaction as the merge.

---

## 🟠 Must Have

> Real bugs or significant quality gaps that hurt usability or reliability.

- [ ] **`datetime.utcnow()` is deprecated in Python 3.12** — Used in every model and router. Raises `DeprecationWarning` on Python 3.12 and will be removed in a future version. Replace all occurrences with `datetime.now(timezone.utc)`.

- [ ] **No file type validation on image upload** — `POST /contacts/{id}/image` passes any `UploadFile` straight to `_process_image()`, which calls `Image.open()`. Uploading a non-image (PDF, text file) causes an unhandled 500 from Pillow. Validate `file.content_type` against an allowlist (`image/jpeg`, `image/png`, `image/webp`, `image/gif`) before processing.

- [ ] **Frontend `JSON.parse` calls are unguarded** — `interactions/[id]/page.tsx:73-74` calls `JSON.parse(summary.action_points)` and `JSON.parse(summary.key_topics)` without a try/catch. If the AI returns malformed JSON the page crashes. Wrap in try/catch and default to `[]`.

- [ ] **No error handling for failed API calls in `useEffect`** — Pages call `Promise.all([...])` with no `.catch()`. A 401 or 500 leaves the component stuck in `loading: true` forever with no user feedback. Add catch handlers and an `error` state that renders a meaningful message.

- [ ] **O(n²) merge scan runs entirely in Python memory** — `score_merge_candidates` loads all non-archived contacts and compares every pair in Python. At 1 000 contacts this is 500 000 string comparisons in a single Celery task; at 10 000 contacts it is 50 million. Pre-filter candidates in SQL (e.g. using `pg_trgm` similarity or matching on first letter of last name) and add a hard contact-count guard.

- [ ] **Polling stops silently after 20 attempts (~60 seconds)** — `interactions/[id]/page.tsx:50` stops polling when `attempts > 20` but only updates the state to whatever the last poll returned. The spinner disappears with no explanation if the worker is slow. Show a clear "took too long — refresh the page" message when the limit is hit.

- [ ] **`/health` endpoint does not check the database or Redis** — Returns `{"status": "ok"}` unconditionally. Orchestrators report the service healthy even when the database is down. Execute a `SELECT 1` and ping Redis; return 503 on failure.

- [ ] **`email_secondary` excluded from merge detection** — `score_merge_candidates` only checks `a.email == b.email`. Two contacts where one's primary email matches the other's `email_secondary` are not flagged as duplicates.

- [ ] **No database connection pool configuration** — `create_engine()` uses SQLAlchemy defaults (`pool_size=5`, `max_overflow=10`). Under concurrent load from uvicorn workers and Celery tasks, PostgreSQL connections will be exhausted. Configure `pool_size`, `max_overflow`, `pool_pre_ping=True`, and `pool_recycle=300`.

- [ ] **No typed Pydantic request/response schemas** — All mutation endpoints accept raw `dict`. FastAPI cannot generate correct OpenAPI docs, validation errors give no field-level messages, and the Swagger UI is useless for these endpoints. Define `ContactCreate`, `ContactUpdate`, `CompanyCreate`, etc.

- [ ] **Interactions are hard-deleted** — `DELETE /interactions/{id}` permanently removes the interaction and its AI summary. Contacts and companies use soft-delete via `is_archived` but interactions do not. Add `is_archived` to `Interaction` or implement soft-delete consistently.

- [ ] **Merge UI has no field selection — always keeps `contact_a`** — `merge/page.tsx:49` calls `mergeContacts(suggestion.contact_a_id, suggestion.contact_b_id, {}, token)` with empty `field_overrides`. The API supports field overrides but the UI never uses them. Users cannot choose which contact's data to keep. Add a side-by-side field comparison UI.

- [ ] **`resolvesuggestion` naming inconsistency in `api.ts`** — `api.ts:136` exports `resolvesuggestion` (all lowercase). Should be `resolveSuggestion` (camelCase) to match every other export in the file.

- [ ] **No company detail page or project detail page** — `companies/[id]/page.tsx` and `projects/[id]/page.tsx` do not exist. Companies are listed but not viewable individually. Projects show a Kanban board but individual projects have no detail view.

- [ ] **Merge scan result polled with a hardcoded 3-second delay** — `merge/page.tsx:40` — `setTimeout(() => { loadSuggestions(token); setScanning(false); }, 3000)`. The scan is queued to Celery and may finish before or after 3 seconds. Poll the existing `GET /contacts/merge-suggestions/scan/{job_id}` endpoint until state is `SUCCESS` instead.

- [ ] **No validation that `contact_id` exists before creating an interaction** — If the UUID is valid format but the contact does not exist, the API creates the interaction and enqueues the Celery task, which then silently returns early. Return 404 upfront.

---

## 🟡 Nice to Have

> UX improvements and code quality issues that are worth addressing after the above.

- [ ] **AI-extracted interaction date should drive `last_contacted_at` + add `last_updated_by` tracking** — Currently `last_contacted_at` is set to the user-supplied `interaction_date` (or `utcnow()`) and never revised. The AI already processes the raw content, which often contains the true communication date (email headers, meeting references, "we spoke on…"). Extend the AI prompt to also extract `interaction_date` from the content. The Celery task should then update `Interaction.interaction_date` and `Contact.last_contacted_at` with the AI-resolved date if it is valid and not in the future. Separately, add `last_updated_at: Optional[datetime]` and `last_updated_by: Optional[str]` columns to `Contact` (populated from JWT `sub` or `email` on every write), so users can see who last touched a record. Requires: prompt change · `ai_tasks.py` post-processing · new migration · `Contact` model update · all contact write paths · `types.ts` update.

- [ ] **No pagination in the frontend** — All list endpoints support `skip`/`limit` but the frontend always fetches the first page and has no load-more or pagination UI. Users with more than 50 contacts silently see a truncated list.

- [ ] **No test suite** — No unit tests, no integration tests, no mocked Anthropic client. The AI task logic, merge scoring, and auth middleware are all untested. Add pytest with at least unit tests for `score_merge_candidates`, `summarise_interaction` (mocked), and the auth dependency.

- [ ] **SWR used inconsistently** — Some pages use SWR, others repeat the `getToken() → useState(token) → useEffect(fetch)` pattern manually. Standardise on SWR with a shared `fetcher` that injects the Bearer token, eliminating the boilerplate.

- [ ] **No loading / disabled states on mutation buttons** — "Merge →", "Reject", "Scan for duplicates", and "Log Interaction" buttons do not disable themselves during in-flight requests, allowing double-submissions.

- [ ] **`create_db_and_tables()` is dead code** — `database.py:12` defines the function but it is never called. Alembic is the source of truth. Remove it to avoid confusion.

- [ ] **No structured logging or request tracing** — The backend has no structured JSON logs, no request ID, and no correlation between an API request and the Celery task it spawns. Add `structlog` or configure `uvicorn` JSON logging, and pass a correlation ID from the API into the Celery task kwargs.

- [ ] **`interaction_ai_summaries` has no `updated_at`** — When a summary is reprocessed via `/reprocess`, `processed_at` is overwritten and there is no history of how many times it ran. Add `updated_at` and consider storing `reprocess_count`.

- [ ] **AI polling uses a fixed 3-second interval** — Replace with exponential backoff (1 s → 2 s → 4 s → 8 s capped at 15 s) to reduce unnecessary API load while the worker is busy.

- [ ] **`from_whom` and `direction` semantics are undocumented and unvalidated** — The `direction` field accepts any string (default `"mutual"`). Neither field is validated against an enum. Define `Literal["inbound", "outbound", "mutual"]` in the model and document what `from_whom` represents.

- [ ] **No feedback when image search returns no candidates** — If `search_contact_images` returns an empty list, the search button spinner simply disappears. Show a "No images found" message to the user.

- [ ] **`pool_pre_ping` not set — stale connections not handled** — Long-running Celery workers hold DB connections that time out at the Supabase/PgBouncer level, causing `OperationalError` on the next query. Enable `pool_pre_ping=True` in `create_engine`.

- [ ] **No Celery Beat for scheduled merge scanning** — Duplicate detection is purely on-demand. Add a nightly Celery Beat schedule for `scan_merge_candidates` so the merge suggestions list stays current without manual intervention.

- [ ] **Interaction polling stops with no user message at attempt limit** — Related to the Must Have above. Even after fixing the message, consider adding a "Reprocess" button directly on the detail page so the user can retry without navigating away.

---

## 🔵 Possible / Future

> Larger features or architectural changes worth considering as the product grows.

- [ ] **Multi-tenancy / team support** — Add `org_id` to all entities (derivable from the `ALLOWED_EMAIL_DOMAIN` restriction) so multiple users sharing an email domain can collaborate on a shared contact/project database, while keeping personal data isolated when needed.

- [ ] **Webhooks / server-sent events for AI completion** — Replace the 3-second polling loop with SSE or a WebSocket connection for real-time AI summary delivery. Alternatively, use the Supabase Realtime channel to push updates when `ai_status` changes in the DB.

- [ ] **Email integration / auto-import** — Parse incoming emails via Gmail or Outlook API and auto-create `Interaction` records. This would make Socii genuinely passive — interactions log themselves.

- [ ] **Periodic AI relationship summaries** — A scheduled Celery Beat task that generates a high-level "relationship health" summary for each contact, synthesising all their interactions rather than summarising them individually.

- [ ] **`pg_trgm` for fuzzy search and merge detection** — Replace the Python `SequenceMatcher` merge scan with SQL-native trigram similarity via the `pg_trgm` extension. Index-supported, no Python memory overhead, and enables real-time duplicate detection at contact creation time.

- [ ] **Search result ranking** — The FTS index on `contacts` and `companies` exists but results are not ranked by relevance. Add `ts_rank` ordering so the most relevant results appear first.

- [ ] **Full data export / import** — CSV and JSON export of all contacts, companies, and projects. Import from common CRM formats (HubSpot export CSV, Salesforce CSV) to lower the barrier to adoption.

- [ ] **Audit log table** — Track every field change with who changed it and when. Essential once multi-tenancy is added and important for debugging data quality issues.

- [ ] **Advanced merge UI with field-by-field selection** — The backend already accepts `field_overrides` in `POST /contacts/merge`. Build a side-by-side diff UI that lets users choose which contact's value to keep for each conflicting field before confirming the merge.

- [ ] **Celery task progress reporting** — Extend the `GET /scan/{job_id}` polling pattern to all long-running tasks and expose a general progress endpoint, allowing the frontend to show meaningful progress bars instead of indeterminate spinners.

- [ ] **Mobile app** — The frontend is web-only. A React Native app (sharing `lib/api.ts` types) or a PWA with offline support would significantly improve usability for on-the-go contact logging.

- [ ] **Email / Slack reminders** — Push reminders to email or Slack at the due date rather than relying on the user to check the reminders page.

- [ ] **Company data enrichment** — Use a data enrichment API (Clearbit, Apollo) or AI to auto-fill `industry`, `size_range`, and `description` from a company's website URL when a new company is created.

---

*Last updated: 2026-03-14*
