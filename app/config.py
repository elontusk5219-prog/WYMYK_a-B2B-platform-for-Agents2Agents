from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/wymyk"
    api_key_header: str = "X-API-Key"
    secret_key: str = "change-me-in-production"
    env: str = "development"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
