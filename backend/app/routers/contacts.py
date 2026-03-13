"""Contacts router — route ordering matters: specific paths BEFORE /{id}."""
import json
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlmodel import Session, select, or_, func
from app.database import get_session
from app.auth import get_current_user
from app.models.contact import Contact, ContactCompany, ContactTag, MergeSuggestion
from app.models.company import Company
from app.models.tag import Tag
from app.models.interaction import Interaction
from app.services.storage import upload_contact_image, delete_contact_image
from app.tasks.ai_tasks import scan_merge_candidates

router = APIRouter(prefix="/contacts", tags=["contacts"])


def _base_query(session: Session, include_archived: bool = False):
    q = select(Contact)
    if not include_archived:
        q = q.where(Contact.is_archived == False)
    return q


# ── SPECIFIC PATHS (must come before /{id}) ────────────────────────────────

@router.get("/needs-contact")
def needs_contact(
    limit: int = Query(20, le=100),
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    """Return contacts sorted by neglect score (days_since / frequency)."""
    contacts = session.exec(
        select(Contact)
        .where(Contact.is_archived == False)
        .order_by(Contact.last_contacted_at.asc().nullsfirst())
        .limit(limit)
    ).all()
    return contacts


@router.post("/check-duplicate")
def check_duplicate(
    body: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    email = body.get("email")
    first_name = body.get("first_name", "")
    last_name = body.get("last_name", "")

    candidates = []
    if email:
        exact = session.exec(select(Contact).where(Contact.email == email)).first()
        if exact:
            candidates.append({"contact": exact, "reason": "same email", "confidence": 1.0})

    name_matches = session.exec(
        select(Contact)
        .where(Contact.first_name.ilike(first_name))
        .where(Contact.last_name.ilike(last_name) if last_name else True)
        .where(Contact.is_archived == False)
        .limit(5)
    ).all()
    for c in name_matches:
        if not any(x["contact"].id == c.id for x in candidates):
            candidates.append({"contact": c, "reason": "similar name", "confidence": 0.7})

    return {"duplicates": candidates}


@router.get("/merge-suggestions")
def list_merge_suggestions(
    status: str = Query("pending"),
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    suggestions = session.exec(
        select(MergeSuggestion).where(MergeSuggestion.status == status)
    ).all()
    return suggestions


@router.post("/merge-suggestions/scan", status_code=202)
def trigger_merge_scan(_user=Depends(get_current_user)):
    task = scan_merge_candidates.delay()
    return {"job_id": task.id, "status": "queued"}


@router.get("/merge-suggestions/scan/{job_id}")
def poll_merge_scan(job_id: str, _user=Depends(get_current_user)):
    from celery.result import AsyncResult
    from app.worker import celery_app
    result = AsyncResult(job_id, app=celery_app)
    return {"job_id": job_id, "state": result.state, "result": result.result if result.ready() else None}


@router.post("/merge")
def merge_contacts(
    body: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    keep_id = uuid.UUID(body["keep_id"])
    discard_id = uuid.UUID(body["discard_id"])
    field_overrides: dict = body.get("field_overrides", {})

    keep = session.get(Contact, keep_id)
    discard = session.get(Contact, discard_id)
    if not keep or not discard:
        raise HTTPException(404, "Contact not found")

    # Apply field overrides
    for field, value in field_overrides.items():
        if hasattr(keep, field):
            setattr(keep, field, value)

    # Re-link interactions
    interactions = session.exec(select(Interaction).where(Interaction.contact_id == discard_id)).all()
    for i in interactions:
        i.contact_id = keep_id
        session.add(i)

    # Union tags
    discard_tags = session.exec(
        select(ContactTag).where(ContactTag.contact_id == discard_id)
    ).all()
    existing_tag_ids = {
        ct.tag_id for ct in session.exec(
            select(ContactTag).where(ContactTag.contact_id == keep_id)
        ).all()
    }
    for ct in discard_tags:
        if ct.tag_id not in existing_tag_ids:
            session.add(ContactTag(contact_id=keep_id, tag_id=ct.tag_id))
        session.delete(ct)

    # Union company links
    discard_companies = session.exec(
        select(ContactCompany).where(ContactCompany.contact_id == discard_id)
    ).all()
    existing_company_ids = {
        cc.company_id for cc in session.exec(
            select(ContactCompany).where(ContactCompany.contact_id == keep_id)
        ).all()
    }
    for cc in discard_companies:
        if cc.company_id not in existing_company_ids:
            session.add(ContactCompany(contact_id=keep_id, company_id=cc.company_id, role=cc.role))
        session.delete(cc)

    session.delete(discard)
    keep.updated_at = datetime.utcnow()
    session.add(keep)
    session.commit()
    session.refresh(keep)
    return keep


@router.patch("/merge-suggestions/{suggestion_id}")
def resolve_merge_suggestion(
    suggestion_id: uuid.UUID,
    body: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    suggestion = session.get(MergeSuggestion, suggestion_id)
    if not suggestion:
        raise HTTPException(404, "Suggestion not found")
    suggestion.status = body.get("status", suggestion.status)
    suggestion.resolved_at = datetime.utcnow()
    session.add(suggestion)
    session.commit()
    return suggestion


# ── GENERIC CRUD ──────────────────────────────────────────────────────────

@router.get("")
def list_contacts(
    q: Optional[str] = None,
    company_id: Optional[uuid.UUID] = None,
    tag_id: Optional[uuid.UUID] = None,
    include_archived: bool = False,
    skip: int = 0,
    limit: int = Query(50, le=200),
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    query = _base_query(session, include_archived)
    if q:
        query = query.where(
            or_(
                Contact.first_name.ilike(f"%{q}%"),
                Contact.last_name.ilike(f"%{q}%"),
                Contact.email.ilike(f"%{q}%"),
            )
        )
    if company_id:
        query = query.join(ContactCompany).where(ContactCompany.company_id == company_id)
    if tag_id:
        query = query.join(ContactTag).where(ContactTag.tag_id == tag_id)
    contacts = session.exec(query.offset(skip).limit(limit)).all()
    return contacts


@router.post("", status_code=201)
def create_contact(
    contact: Contact,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    contact.id = uuid.uuid4()
    contact.created_at = datetime.utcnow()
    contact.updated_at = datetime.utcnow()
    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact


@router.get("/{contact_id}")
def get_contact(
    contact_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(404, "Contact not found")
    return contact


@router.put("/{contact_id}")
def update_contact(
    contact_id: uuid.UUID,
    data: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(404, "Contact not found")
    for k, v in data.items():
        if hasattr(contact, k) and k not in ("id", "created_at"):
            setattr(contact, k, v)
    contact.updated_at = datetime.utcnow()
    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact


@router.patch("/{contact_id}")
def patch_contact(
    contact_id: uuid.UUID,
    data: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    return update_contact(contact_id, data, session, _user)


@router.delete("/{contact_id}", status_code=204)
def delete_contact(
    contact_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(404, "Contact not found")
    contact.is_archived = True
    contact.updated_at = datetime.utcnow()
    session.add(contact)
    session.commit()


@router.post("/{contact_id}/image")
async def upload_image(
    contact_id: uuid.UUID,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(404, "Contact not found")
    url, path = await upload_contact_image(str(contact_id), file)
    contact.image_url = url
    contact.image_storage_path = path
    contact.updated_at = datetime.utcnow()
    session.add(contact)
    session.commit()
    return {"image_url": url}


@router.delete("/{contact_id}/image", status_code=204)
async def remove_image(
    contact_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    contact = session.get(Contact, contact_id)
    if not contact or not contact.image_storage_path:
        raise HTTPException(404, "Contact or image not found")
    await delete_contact_image(contact.image_storage_path)
    contact.image_url = None
    contact.image_storage_path = None
    contact.updated_at = datetime.utcnow()
    session.add(contact)
    session.commit()


@router.get("/{contact_id}/timeline")
def contact_timeline(
    contact_id: uuid.UUID,
    skip: int = 0,
    limit: int = Query(50, le=200),
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(404, "Contact not found")
    interactions = session.exec(
        select(Interaction)
        .where(Interaction.contact_id == contact_id)
        .order_by(Interaction.interaction_date.desc())
        .offset(skip)
        .limit(limit)
    ).all()
    return interactions


@router.post("/{contact_id}/image/search")
async def image_search(
    contact_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    from app.services.image_search import search_contact_images
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(404, "Contact not found")
    candidates = await search_contact_images(contact)
    return {"candidates": candidates}


@router.post("/{contact_id}/image/import")
async def image_import(
    contact_id: uuid.UUID,
    body: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    from app.services.image_search import import_image_from_url
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(404, "Contact not found")
    url, path = await import_image_from_url(body["url"], f"contacts/{contact_id}/avatar.webp")
    contact.image_url = url
    contact.image_storage_path = path
    contact.updated_at = datetime.utcnow()
    session.add(contact)
    session.commit()
    return {"image_url": url}


@router.post("/{contact_id}/tags/{tag_id}", status_code=201)
def add_tag(
    contact_id: uuid.UUID,
    tag_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    existing = session.exec(
        select(ContactTag)
        .where(ContactTag.contact_id == contact_id, ContactTag.tag_id == tag_id)
    ).first()
    if not existing:
        session.add(ContactTag(contact_id=contact_id, tag_id=tag_id))
        session.commit()
    return {"status": "ok"}


@router.delete("/{contact_id}/tags/{tag_id}", status_code=204)
def remove_tag(
    contact_id: uuid.UUID,
    tag_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    ct = session.exec(
        select(ContactTag)
        .where(ContactTag.contact_id == contact_id, ContactTag.tag_id == tag_id)
    ).first()
    if ct:
        session.delete(ct)
        session.commit()
