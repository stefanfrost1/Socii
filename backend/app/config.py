from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_database_url: str
    supabase_url: str
    supabase_key: str
    anthropic_api_key: str
    redis_url: str = "redis://redis:6379/0"
    allowed_email_domain: str = "simplitics.se"

    class Config:
        env_file = ".env"


settings = Settings()
