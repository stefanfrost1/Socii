import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlmodel import Session, select
from app.database import get_session
from app.auth import get_current_user
from app.models.company import Company, CompanyTag
from app.models.contact import Contact, ContactCompany
from app.models.project import Project, ProjectCompany
from app.models.tag import Tag
from app.services.storage import upload_company_logo, delete_company_logo

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("")
def list_companies(
    q: Optional[str] = None,
    tag_id: Optional[uuid.UUID] = None,
    include_archived: bool = False,
    skip: int = 0,
    limit: int = Query(50, le=200),
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    query = select(Company)
    if not include_archived:
        query = query.where(Company.is_archived == False)
    if q:
        query = query.where(Company.name.ilike(f"%{q}%"))
    if tag_id:
        query = query.join(CompanyTag).where(CompanyTag.tag_id == tag_id)
    return session.exec(query.offset(skip).limit(limit)).all()


@router.post("", status_code=201)
def create_company(
    company: Company,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    company.id = uuid.uuid4()
    company.created_at = datetime.utcnow()
    company.updated_at = datetime.utcnow()
    session.add(company)
    session.commit()
    session.refresh(company)
    return company


@router.get("/{company_id}")
def get_company(
    company_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    return company


@router.put("/{company_id}")
def update_company(
    company_id: uuid.UUID,
    data: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    for k, v in data.items():
        if hasattr(company, k) and k not in ("id", "created_at"):
            setattr(company, k, v)
    company.updated_at = datetime.utcnow()
    session.add(company)
    session.commit()
    session.refresh(company)
    return company


@router.patch("/{company_id}")
def patch_company(
    company_id: uuid.UUID,
    data: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    return update_company(company_id, data, session, _user)


@router.delete("/{company_id}", status_code=204)
def delete_company(
    company_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    company.is_archived = True
    company.updated_at = datetime.utcnow()
    session.add(company)
    session.commit()


@router.post("/{company_id}/logo")
async def upload_logo(
    company_id: uuid.UUID,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    url, path = await upload_company_logo(str(company_id), file)
    company.logo_url = url
    company.logo_storage_path = path
    company.updated_at = datetime.utcnow()
    session.add(company)
    session.commit()
    return {"logo_url": url}


@router.get("/{company_id}/contacts")
def company_contacts(
    company_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    contacts = session.exec(
        select(Contact)
        .join(ContactCompany)
        .where(ContactCompany.company_id == company_id)
        .where(Contact.is_archived == False)
    ).all()
    return contacts


@router.get("/{company_id}/projects")
def company_projects(
    company_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    projects = session.exec(
        select(Project)
        .join(ProjectCompany)
        .where(ProjectCompany.company_id == company_id)
        .where(Project.is_archived == False)
    ).all()
    return projects


@router.post("/{company_id}/logo/search")
async def logo_search(
    company_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    from app.services.image_search import search_company_logo
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    candidates = await search_company_logo(company)
    return {"candidates": candidates}


@router.post("/{company_id}/logo/import")
async def logo_import(
    company_id: uuid.UUID,
    body: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    from app.services.image_search import import_image_from_url
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    url, path = await import_image_from_url(body["url"], f"companies/{company_id}/logo.webp")
    company.logo_url = url
    company.logo_storage_path = path
    company.updated_at = datetime.utcnow()
    session.add(company)
    session.commit()
    return {"logo_url": url}


@router.post("/{company_id}/tags/{tag_id}", status_code=201)
def add_tag(
    company_id: uuid.UUID,
    tag_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    existing = session.exec(
        select(CompanyTag)
        .where(CompanyTag.company_id == company_id, CompanyTag.tag_id == tag_id)
    ).first()
    if not existing:
        session.add(CompanyTag(company_id=company_id, tag_id=tag_id))
        session.commit()
    return {"status": "ok"}


@router.delete("/{company_id}/tags/{tag_id}", status_code=204)
def remove_tag(
    company_id: uuid.UUID,
    tag_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    ct = session.exec(
        select(CompanyTag)
        .where(CompanyTag.company_id == company_id, CompanyTag.tag_id == tag_id)
    ).first()
    if ct:
        session.delete(ct)
        session.commit()
