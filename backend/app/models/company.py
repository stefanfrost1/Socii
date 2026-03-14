import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Company(SQLModel, table=True):
    __tablename__ = "companies"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    website_url: Optional[str] = Field(default=None)
    linkedin_url: Optional[str] = Field(default=None)
    industry: Optional[str] = Field(default=None, max_length=100)
    size_range: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None)
    logo_url: Optional[str] = Field(default=None)
    logo_storage_path: Optional[str] = Field(default=None)
    address_city: Optional[str] = Field(default=None, max_length=100)
    address_country: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_archived: bool = Field(default=False, index=True)


class CompanyTag(SQLModel, table=True):
    __tablename__ = "company_tags"

    company_id: uuid.UUID = Field(foreign_key="companies.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)
