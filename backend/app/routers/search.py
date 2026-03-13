from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, text
from app.database import get_session
from app.auth import get_current_user

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def global_search(
    q: str = Query(..., min_length=2),
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    if not q.strip():
        return {"contacts": [], "companies": [], "projects": []}

    ts_query = " & ".join(q.strip().split())
    pattern = f"%{q}%"

    contacts = session.exec(
        text("""
            SELECT id, first_name, last_name, email, title, image_url
            FROM contacts
            WHERE is_archived = false
              AND (fts @@ to_tsquery('english', :tsq)
                   OR first_name ILIKE :pat
                   OR last_name ILIKE :pat
                   OR email ILIKE :pat)
            LIMIT 10
        """),
        {"tsq": ts_query, "pat": pattern},
    ).mappings().all()

    companies = session.exec(
        text("""
            SELECT id, name, industry, logo_url
            FROM companies
            WHERE is_archived = false
              AND (fts @@ to_tsquery('english', :tsq) OR name ILIKE :pat)
            LIMIT 10
        """),
        {"tsq": ts_query, "pat": pattern},
    ).mappings().all()

    projects = session.exec(
        text("""
            SELECT p.id, p.name, p.description, ps.name as stage_name
            FROM projects p
            LEFT JOIN project_stages ps ON p.stage_id = ps.id
            WHERE p.is_archived = false
              AND (p.name ILIKE :pat OR p.description ILIKE :pat)
            LIMIT 10
        """),
        {"pat": pattern},
    ).mappings().all()

    return {
        "contacts": [dict(r) for r in contacts],
        "companies": [dict(r) for r in companies],
        "projects": [dict(r) for r in projects],
    }
