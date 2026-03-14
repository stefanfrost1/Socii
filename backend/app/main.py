from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import contacts, companies, projects, interactions, stages, tags, reminders, search, dashboard, auth
from app.config import settings

app = FastAPI(title="Socii CRM API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PREFIX = "/api/v1"

app.include_router(auth.router, prefix=PREFIX)
app.include_router(dashboard.router, prefix=PREFIX)
app.include_router(contacts.router, prefix=PREFIX)
app.include_router(companies.router, prefix=PREFIX)
app.include_router(projects.router, prefix=PREFIX)
app.include_router(interactions.router, prefix=PREFIX)
app.include_router(stages.router, prefix=PREFIX)
app.include_router(tags.router, prefix=PREFIX)
app.include_router(reminders.router, prefix=PREFIX)
app.include_router(search.router, prefix=PREFIX)


@app.get("/health")
def health():
    return {"status": "ok"}
