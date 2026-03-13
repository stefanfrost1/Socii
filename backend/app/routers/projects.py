import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.database import get_session
from app.auth import get_current_user
from app.models.project import Project, ProjectContact, ProjectCompany, ProjectStage, ProjectTag
from app.models.tag import Tag

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
def list_projects(
    stage_id: Optional[uuid.UUID] = None,
    tag_id: Optional[uuid.UUID] = None,
    include_archived: bool = False,
    skip: int = 0,
    limit: int = Query(100, le=500),
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    query = select(Project)
    if not include_archived:
        query = query.where(Project.is_archived == False)
    if stage_id:
        query = query.where(Project.stage_id == stage_id)
    if tag_id:
        query = query.join(ProjectTag).where(ProjectTag.tag_id == tag_id)
    return session.exec(query.offset(skip).limit(limit)).all()


@router.post("", status_code=201)
def create_project(
    project: Project,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    project.id = uuid.uuid4()
    project.created_at = datetime.utcnow()
    project.updated_at = datetime.utcnow()
    if project.stage_id:
        project.stage_updated_at = datetime.utcnow()
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.get("/{project_id}")
def get_project(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.put("/{project_id}")
def update_project(
    project_id: uuid.UUID,
    data: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    old_stage = project.stage_id
    for k, v in data.items():
        if hasattr(project, k) and k not in ("id", "created_at"):
            setattr(project, k, v)
    if project.stage_id != old_stage:
        project.stage_updated_at = datetime.utcnow()
    project.updated_at = datetime.utcnow()
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.patch("/{project_id}")
def patch_project(
    project_id: uuid.UUID,
    data: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    return update_project(project_id, data, session, _user)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    project.is_archived = True
    project.updated_at = datetime.utcnow()
    session.add(project)
    session.commit()


@router.post("/{project_id}/contacts", status_code=201)
def link_contact(
    project_id: uuid.UUID,
    body: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    contact_id = uuid.UUID(body["contact_id"])
    role = body.get("role")
    existing = session.exec(
        select(ProjectContact)
        .where(ProjectContact.project_id == project_id, ProjectContact.contact_id == contact_id)
    ).first()
    if not existing:
        session.add(ProjectContact(project_id=project_id, contact_id=contact_id, role=role))
        session.commit()
    return {"status": "ok"}


@router.delete("/{project_id}/contacts/{contact_id}", status_code=204)
def unlink_contact(
    project_id: uuid.UUID,
    contact_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    pc = session.exec(
        select(ProjectContact)
        .where(ProjectContact.project_id == project_id, ProjectContact.contact_id == contact_id)
    ).first()
    if pc:
        session.delete(pc)
        session.commit()


@router.post("/{project_id}/companies", status_code=201)
def link_company(
    project_id: uuid.UUID,
    body: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    company_id = uuid.UUID(body["company_id"])
    existing = session.exec(
        select(ProjectCompany)
        .where(ProjectCompany.project_id == project_id, ProjectCompany.company_id == company_id)
    ).first()
    if not existing:
        session.add(ProjectCompany(project_id=project_id, company_id=company_id))
        session.commit()
    return {"status": "ok"}


@router.delete("/{project_id}/companies/{company_id}", status_code=204)
def unlink_company(
    project_id: uuid.UUID,
    company_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    pc = session.exec(
        select(ProjectCompany)
        .where(ProjectCompany.project_id == project_id, ProjectCompany.company_id == company_id)
    ).first()
    if pc:
        session.delete(pc)
        session.commit()


@router.post("/{project_id}/tags/{tag_id}", status_code=201)
def add_tag(
    project_id: uuid.UUID,
    tag_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    existing = session.exec(
        select(ProjectTag)
        .where(ProjectTag.project_id == project_id, ProjectTag.tag_id == tag_id)
    ).first()
    if not existing:
        session.add(ProjectTag(project_id=project_id, tag_id=tag_id))
        session.commit()
    return {"status": "ok"}


@router.delete("/{project_id}/tags/{tag_id}", status_code=204)
def remove_tag(
    project_id: uuid.UUID,
    tag_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    pt = session.exec(
        select(ProjectTag)
        .where(ProjectTag.project_id == project_id, ProjectTag.tag_id == tag_id)
    ).first()
    if pt:
        session.delete(pt)
        session.commit()
