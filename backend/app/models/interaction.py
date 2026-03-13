import uuid
from datetime import date, datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Interaction(SQLModel, table=True):
    __tablename__ = "interactions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    contact_id: uuid.UUID = Field(foreign_key="contacts.id", index=True)
    project_id: Optional[uuid.UUID] = Field(default=None, foreign_key="projects.id", index=True)
    raw_content: str = Field()
    interaction_type: str = Field(default="other", max_length=50)
    interaction_date: datetime = Field(default_factory=datetime.utcnow, index=True)
    direction: str = Field(default="mutual", max_length=10)
    from_whom: Optional[str] = Field(default=None, max_length=200)
    ai_status: str = Field(default="pending", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InteractionAISummary(SQLModel, table=True):
    __tablename__ = "interaction_ai_summaries"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    interaction_id: uuid.UUID = Field(foreign_key="interactions.id", unique=True, index=True)
    summary: Optional[str] = Field(default=None)
    action_points: Optional[str] = Field(default=None)  # JSON
    follow_up_date: Optional[date] = Field(default=None)
    key_topics: Optional[str] = Field(default=None)  # JSON array
    sentiment: Optional[str] = Field(default=None, max_length=20)
    model_used: Optional[str] = Field(default=None, max_length=50)
    prompt_version: int = Field(default=1)
    processed_at: Optional[datetime] = Field(default=None)
    raw_response: Optional[str] = Field(default=None)  # JSON
