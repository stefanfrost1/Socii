import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.database import get_session
from app.auth import get_current_user
from app.models.reminder import Reminder

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("")
def list_reminders(
    contact_id: uuid.UUID = None,
    project_id: uuid.UUID = None,
    completed: bool = False,
    skip: int = 0,
    limit: int = Query(100, le=500),
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    query = select(Reminder).where(Reminder.is_completed == completed)
    if contact_id:
        query = query.where(Reminder.contact_id == contact_id)
    if project_id:
        query = query.where(Reminder.project_id == project_id)
    query = query.order_by(Reminder.due_date.asc().nullslast())
    return session.exec(query.offset(skip).limit(limit)).all()


@router.post("", status_code=201)
def create_reminder(
    reminder: Reminder,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    reminder.id = uuid.uuid4()
    reminder.created_at = datetime.utcnow()
    session.add(reminder)
    session.commit()
    session.refresh(reminder)
    return reminder


@router.patch("/{reminder_id}")
def update_reminder(
    reminder_id: uuid.UUID,
    body: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    reminder = session.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(404, "Reminder not found")
    for k, v in body.items():
        if hasattr(reminder, k) and k not in ("id", "created_at"):
            setattr(reminder, k, v)
    if body.get("is_completed") and not reminder.completed_at:
        reminder.completed_at = datetime.utcnow()
    session.add(reminder)
    session.commit()
    session.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", status_code=204)
def delete_reminder(
    reminder_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    reminder = session.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(404, "Reminder not found")
    session.delete(reminder)
    session.commit()
