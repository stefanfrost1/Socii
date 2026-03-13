from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func, text
from app.database import get_session
from app.auth import get_current_user
from app.models.interaction import Interaction, InteractionAISummary
from app.models.contact import Contact
from app.models.project import Project, ProjectStage
from app.models.reminder import Reminder
from datetime import date

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def overview(
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    # Recent interactions (last 20) with AI summaries
    recent_interactions = session.exec(
        select(Interaction)
        .where(Interaction.contact_id != None)
        .order_by(Interaction.interaction_date.desc())
        .limit(20)
    ).all()

    interaction_ids = [str(i.id) for i in recent_interactions]
    summaries = {}
    if interaction_ids:
        ai_summaries = session.exec(
            select(InteractionAISummary).where(
                InteractionAISummary.interaction_id.in_([i.id for i in recent_interactions])
            )
        ).all()
        summaries = {str(s.interaction_id): s for s in ai_summaries}

    # Pipeline summary by stage
    pipeline = session.exec(
        select(ProjectStage, func.count(Project.id).label("count"))
        .outerjoin(Project, (Project.stage_id == ProjectStage.id) & (Project.is_archived == False))
        .group_by(ProjectStage.id)
        .order_by(ProjectStage.order_index)
    ).all()

    # Needs contact — top 20 most overdue
    needs_contact = session.exec(
        select(Contact)
        .where(Contact.is_archived == False)
        .order_by(Contact.last_contacted_at.asc().nullsfirst())
        .limit(20)
    ).all()

    # Due today reminders
    today = date.today()
    due_today = session.exec(
        select(Reminder)
        .where(Reminder.due_date == today, Reminder.is_completed == False)
        .limit(10)
    ).all()

    return {
        "recent_interactions": [
            {
                "interaction": i,
                "ai_summary": summaries.get(str(i.id)),
            }
            for i in recent_interactions
        ],
        "pipeline": [
            {"stage": stage, "count": count}
            for stage, count in pipeline
        ],
        "needs_contact": needs_contact,
        "due_today": due_today,
    }
