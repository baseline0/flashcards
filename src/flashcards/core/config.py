import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration."""

    app_name: str = "Flashcards"
    debug: bool = False
    database_url: str = "sqlite:///./data/flashcards.sqlite"
    glossaries_path: Path = Path("data/raw_glossaries")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
