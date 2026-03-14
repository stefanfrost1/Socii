from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

engine = create_engine(settings.supabase_database_url, echo=False)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
