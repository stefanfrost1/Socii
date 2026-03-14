import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.auth import get_current_user
from app.models.tag import Tag

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("")
def list_tags(
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    return session.exec(select(Tag).order_by(Tag.name)).all()


@router.post("", status_code=201)
def create_tag(
    tag: Tag,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    existing = session.exec(select(Tag).where(Tag.name == tag.name)).first()
    if existing:
        raise HTTPException(400, f"Tag '{tag.name}' already exists")
    tag.id = uuid.uuid4()
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(
    tag_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(404, "Tag not found")
    session.delete(tag)
    session.commit()
