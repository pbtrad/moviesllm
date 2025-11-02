from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = "sqlite:///./movies.db"

    llm_provider: str = "openai"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"


settings = Settings()