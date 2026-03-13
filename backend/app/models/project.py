import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class ProjectStage(SQLModel, table=True):
    __tablename__ = "project_stages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=100)
    order_index: int = Field(default=0)
    color: str = Field(default="#6B7280", max_length=7)
    is_terminal: bool = Field(default=False)
    is_default: bool = Field(default=False)


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None)
    stage_id: Optional[uuid.UUID] = Field(default=None, foreign_key="project_stages.id")
    stage_updated_at: Optional[datetime] = Field(default=None)
    value_estimate: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12)
    currency: str = Field(default="USD", max_length=3)
    close_date_target: Optional[date] = Field(default=None)
    close_date_actual: Optional[date] = Field(default=None)
    outcome: Optional[str] = Field(default=None, max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_archived: bool = Field(default=False, index=True)


class ProjectContact(SQLModel, table=True):
    __tablename__ = "project_contacts"

    project_id: uuid.UUID = Field(foreign_key="projects.id", primary_key=True)
    contact_id: uuid.UUID = Field(foreign_key="contacts.id", primary_key=True)
    role: Optional[str] = Field(default=None, max_length=100)


class ProjectCompany(SQLModel, table=True):
    __tablename__ = "project_companies"

    project_id: uuid.UUID = Field(foreign_key="projects.id", primary_key=True)
    company_id: uuid.UUID = Field(foreign_key="companies.id", primary_key=True)


class ProjectTag(SQLModel, table=True):
    __tablename__ = "project_tags"

    project_id: uuid.UUID = Field(foreign_key="projects.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)
