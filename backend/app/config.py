from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_database_url: str
    supabase_url: str
    supabase_key: str
    anthropic_api_key: str
    redis_url: str = "redis://redis:6379/0"
    allowed_email_domain: str = "simplitics.se"
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
