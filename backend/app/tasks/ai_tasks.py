"""Celery tasks for AI processing."""
import json
import uuid
from datetime import datetime, date
from app.worker import celery_app


@celery_app.task(
    name="process_interaction_ai",
    queue="interactions_ai",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=900,
    max_retries=3,
)
def process_interaction_ai(interaction_id: str):
    from sqlmodel import Session, select
    from app.database import engine
    from app.models.interaction import Interaction, InteractionAISummary
    from app.models.contact import Contact
    from app.models.reminder import Reminder
    from app.services.ai import summarise_interaction, PROMPT_VERSION

    with Session(engine) as session:
        interaction = session.get(Interaction, uuid.UUID(interaction_id))
        if not interaction:
            return

        interaction.ai_status = "processing"
        session.add(interaction)
        session.commit()

        contact = session.get(Contact, interaction.contact_id)
        contact_name = f"{contact.first_name} {contact.last_name or ''}".strip() if contact else ""

        try:
            result = summarise_interaction(interaction.raw_content, contact_name)
        except Exception as exc:
            interaction.ai_status = "failed"
            session.add(interaction)
            session.commit()
            raise exc

        # Upsert AI summary
        existing = session.exec(
            select(InteractionAISummary).where(InteractionAISummary.interaction_id == interaction.id)
        ).first()
        summary = existing or InteractionAISummary(
            id=uuid.uuid4(),
            interaction_id=interaction.id,
        )
        summary.summary = result.get("summary")
        summary.action_points = json.dumps(result.get("action_points", []))
        summary.key_topics = json.dumps(result.get("key_topics", []))
        summary.sentiment = result.get("sentiment")
        summary.model_used = result.get("_model_used")
        summary.prompt_version = PROMPT_VERSION
        summary.processed_at = datetime.utcnow()
        summary.raw_response = result.get("_raw_response")

        follow_up_str = result.get("follow_up_date")
        if follow_up_str:
            try:
                summary.follow_up_date = date.fromisoformat(follow_up_str)
            except ValueError:
                pass

        session.add(summary)

        # Auto-create reminders for action points that have due_dates
        action_points = result.get("action_points", [])
        for ap in action_points:
            if ap.get("due_date"):
                try:
                    due = date.fromisoformat(ap["due_date"])
                    reminder = Reminder(
                        id=uuid.uuid4(),
                        contact_id=interaction.contact_id,
                        project_id=interaction.project_id,
                        interaction_id=interaction.id,
                        text=ap["text"],
                        due_date=due,
                        created_at=datetime.utcnow(),
                    )
                    session.add(reminder)
                except ValueError:
                    pass

        interaction.ai_status = "done"
        session.add(interaction)
        session.commit()


@celery_app.task(
    name="scan_merge_candidates",
    queue="merge_scan",
)
def scan_merge_candidates():
    from sqlmodel import Session, select
    from app.database import engine
    from app.models.contact import Contact, MergeSuggestion
    from app.services.ai import score_merge_candidates

    with Session(engine) as session:
        contacts = session.exec(
            select(Contact).where(Contact.is_archived == False)
        ).all()

        suggestions = score_merge_candidates(contacts)

        for s in suggestions:
            # Skip already existing pending suggestions for this pair
            existing = session.exec(
                select(MergeSuggestion).where(
                    (
                        (MergeSuggestion.contact_a_id == uuid.UUID(s["contact_a_id"])) &
                        (MergeSuggestion.contact_b_id == uuid.UUID(s["contact_b_id"]))
                    ) | (
                        (MergeSuggestion.contact_a_id == uuid.UUID(s["contact_b_id"])) &
                        (MergeSuggestion.contact_b_id == uuid.UUID(s["contact_a_id"]))
                    )
                ).where(MergeSuggestion.status == "pending")
            ).first()
            if not existing:
                session.add(MergeSuggestion(
                    id=uuid.uuid4(),
                    contact_a_id=uuid.UUID(s["contact_a_id"]),
                    contact_b_id=uuid.UUID(s["contact_b_id"]),
                    confidence_score=s["confidence_score"],
                    reasons=s["reasons"],
                    created_at=datetime.utcnow(),
                ))
        session.commit()
        return {"scanned": len(contacts), "new_suggestions": len(suggestions)}
