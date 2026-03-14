import uuid
from datetime import date, datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Reminder(SQLModel, table=True):
    __tablename__ = "reminders"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    contact_id: Optional[uuid.UUID] = Field(default=None, foreign_key="contacts.id", index=True)
    project_id: Optional[uuid.UUID] = Field(default=None, foreign_key="projects.id")
    interaction_id: Optional[uuid.UUID] = Field(default=None, foreign_key="interactions.id")
    text: str = Field()
    due_date: Optional[date] = Field(default=None, index=True)
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
