import uuid
from datetime import date, datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Contact(SQLModel, table=True):
    __tablename__ = "contacts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    first_name: str = Field(max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[str] = Field(default=None, max_length=255, unique=True, index=True)
    email_secondary: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)
    phone_secondary: Optional[str] = Field(default=None, max_length=50)
    title: Optional[str] = Field(default=None, max_length=100)
    image_url: Optional[str] = Field(default=None)
    image_storage_path: Optional[str] = Field(default=None)
    linkedin_url: Optional[str] = Field(default=None)
    twitter_url: Optional[str] = Field(default=None)
    github_url: Optional[str] = Field(default=None)
    instagram_url: Optional[str] = Field(default=None)
    website_url: Optional[str] = Field(default=None)
    address_city: Optional[str] = Field(default=None, max_length=100)
    address_country: Optional[str] = Field(default=None, max_length=100)
    birthday: Optional[date] = Field(default=None)
    bio_notes: Optional[str] = Field(default=None)
    last_contacted_at: Optional[datetime] = Field(default=None, index=True)
    contact_frequency_days: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_archived: bool = Field(default=False, index=True)


class ContactCompany(SQLModel, table=True):
    __tablename__ = "contact_companies"

    contact_id: uuid.UUID = Field(foreign_key="contacts.id", primary_key=True)
    company_id: uuid.UUID = Field(foreign_key="companies.id", primary_key=True)
    role: Optional[str] = Field(default=None, max_length=100)
    is_primary: bool = Field(default=False)
    started_at: Optional[date] = Field(default=None)
    ended_at: Optional[date] = Field(default=None)


class ContactTag(SQLModel, table=True):
    __tablename__ = "contact_tags"

    contact_id: uuid.UUID = Field(foreign_key="contacts.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)


class MergeSuggestion(SQLModel, table=True):
    __tablename__ = "contact_merge_suggestions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    contact_a_id: uuid.UUID = Field(foreign_key="contacts.id", index=True)
    contact_b_id: uuid.UUID = Field(foreign_key="contacts.id", index=True)
    confidence_score: float = Field(default=0.0)
    reasons: Optional[str] = Field(default=None)  # JSON stored as text
    status: str = Field(default="pending", max_length=20)
    resolved_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
