import json
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.database import get_session
from app.auth import get_current_user
from app.models.interaction import Interaction, InteractionAISummary
from app.models.contact import Contact
from app.tasks.ai_tasks import process_interaction_ai

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("", status_code=201)
def create_interaction(
    body: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    raw = body.get("raw_content", "")
    if len(raw) < 20:
        raise HTTPException(400, "raw_content must be at least 20 characters")

    interaction = Interaction(
        id=uuid.uuid4(),
        contact_id=uuid.UUID(body["contact_id"]),
        project_id=uuid.UUID(body["project_id"]) if body.get("project_id") else None,
        raw_content=raw,
        interaction_type=body.get("interaction_type", "other"),
        interaction_date=datetime.fromisoformat(body["interaction_date"]) if body.get("interaction_date") else datetime.utcnow(),
        direction=body.get("direction", "mutual"),
        from_whom=body.get("from_whom"),
        ai_status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(interaction)

    # Update last_contacted_at on the contact
    contact = session.get(Contact, interaction.contact_id)
    if contact:
        if not contact.last_contacted_at or contact.last_contacted_at < interaction.interaction_date:
            contact.last_contacted_at = interaction.interaction_date
            contact.updated_at = datetime.utcnow()
            session.add(contact)

    session.commit()
    session.refresh(interaction)

    # Enqueue AI processing
    process_interaction_ai.delay(str(interaction.id))

    return interaction


@router.get("/{interaction_id}")
def get_interaction(
    interaction_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    interaction = session.get(Interaction, interaction_id)
    if not interaction:
        raise HTTPException(404, "Interaction not found")
    summary = session.exec(
        select(InteractionAISummary).where(InteractionAISummary.interaction_id == interaction_id)
    ).first()
    return {"interaction": interaction, "ai_summary": summary}


@router.get("/{interaction_id}/ai-summary")
def poll_ai_summary(
    interaction_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    interaction = session.get(Interaction, interaction_id)
    if not interaction:
        raise HTTPException(404, "Interaction not found")
    if interaction.ai_status == "pending" or interaction.ai_status == "processing":
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=202, content={"status": interaction.ai_status})
    summary = session.exec(
        select(InteractionAISummary).where(InteractionAISummary.interaction_id == interaction_id)
    ).first()
    return {"status": interaction.ai_status, "summary": summary}


@router.put("/{interaction_id}")
def update_interaction(
    interaction_id: uuid.UUID,
    body: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    interaction = session.get(Interaction, interaction_id)
    if not interaction:
        raise HTTPException(404, "Interaction not found")
    for k, v in body.items():
        if hasattr(interaction, k) and k not in ("id", "created_at"):
            setattr(interaction, k, v)
    interaction.ai_status = "pending"
    interaction.updated_at = datetime.utcnow()
    session.add(interaction)
    session.commit()
    process_interaction_ai.delay(str(interaction.id))
    session.refresh(interaction)
    return interaction


@router.delete("/{interaction_id}", status_code=204)
def delete_interaction(
    interaction_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    interaction = session.get(Interaction, interaction_id)
    if not interaction:
        raise HTTPException(404, "Interaction not found")
    # Delete AI summary first
    summary = session.exec(
        select(InteractionAISummary).where(InteractionAISummary.interaction_id == interaction_id)
    ).first()
    if summary:
        session.delete(summary)
    session.delete(interaction)
    session.commit()


@router.post("/{interaction_id}/reprocess", status_code=202)
def reprocess(
    interaction_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    interaction = session.get(Interaction, interaction_id)
    if not interaction:
        raise HTTPException(404, "Interaction not found")
    interaction.ai_status = "pending"
    interaction.updated_at = datetime.utcnow()
    session.add(interaction)
    session.commit()
    process_interaction_ai.delay(str(interaction.id))
    return {"status": "queued"}


@router.patch("/{interaction_id}/action-points/{ap_index}")
def toggle_action_point(
    interaction_id: uuid.UUID,
    ap_index: int,
    body: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    summary = session.exec(
        select(InteractionAISummary).where(InteractionAISummary.interaction_id == interaction_id)
    ).first()
    if not summary or not summary.action_points:
        raise HTTPException(404, "AI summary or action points not found")
    points = json.loads(summary.action_points)
    if ap_index >= len(points):
        raise HTTPException(404, "Action point index out of range")
    points[ap_index]["completed"] = body.get("completed", not points[ap_index].get("completed", False))
    if points[ap_index]["completed"]:
        points[ap_index]["completed_at"] = datetime.utcnow().isoformat()
    summary.action_points = json.dumps(points)
    session.add(summary)
    session.commit()
    return points[ap_index]
