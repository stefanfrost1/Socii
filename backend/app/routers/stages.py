import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.auth import get_current_user
from app.models.project import ProjectStage, Project

router = APIRouter(prefix="/stages", tags=["stages"])


@router.get("")
def list_stages(
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    return session.exec(select(ProjectStage).order_by(ProjectStage.order_index)).all()


@router.post("", status_code=201)
def create_stage(
    stage: ProjectStage,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    stage.id = uuid.uuid4()
    session.add(stage)
    session.commit()
    session.refresh(stage)
    return stage


@router.put("/{stage_id}")
def update_stage(
    stage_id: uuid.UUID,
    data: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    stage = session.get(ProjectStage, stage_id)
    if not stage:
        raise HTTPException(404, "Stage not found")
    for k, v in data.items():
        if hasattr(stage, k) and k != "id":
            setattr(stage, k, v)
    session.add(stage)
    session.commit()
    session.refresh(stage)
    return stage


@router.delete("/{stage_id}", status_code=204)
def delete_stage(
    stage_id: uuid.UUID,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    active = session.exec(
        select(Project).where(Project.stage_id == stage_id, Project.is_archived == False)
    ).first()
    if active:
        raise HTTPException(400, "Cannot delete stage with active projects")
    stage = session.get(ProjectStage, stage_id)
    if not stage:
        raise HTTPException(404, "Stage not found")
    session.delete(stage)
    session.commit()


@router.post("/reorder")
def reorder_stages(
    body: dict,
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    """Accepts {order: [{id, order_index}]}"""
    for item in body.get("order", []):
        stage = session.get(ProjectStage, uuid.UUID(item["id"]))
        if stage:
            stage.order_index = item["order_index"]
            session.add(stage)
    session.commit()
    return session.exec(select(ProjectStage).order_by(ProjectStage.order_index)).all()
