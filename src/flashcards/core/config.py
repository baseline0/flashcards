from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration."""

    app_name: str = "Flashcards"
    debug: bool = False
    database_url: str = "sqlite:///./data/flashcards.sqlite"
    glossaries_path: Path = Path("data/raw_glossaries")
    composite_decks_path: Path = Path("data/composite_decks")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
