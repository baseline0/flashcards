from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CardType(str, Enum):
    """Types of flashcards supported."""

    TERM_DEFINITION = "term_definition"
    CLOZE_DELETION = "cloze_deletion"
    QUOTE_ATTRIBUTION = "quote_attribution"


class GlossaryEntry(BaseModel):
    """Raw input: glossary entry from any domain."""

    id: str | None = None
    domain: str
    category: str
    title: str
    body: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Flashcard(BaseModel):
    """Generated card ready for review."""

    id: str | None = None
    entry_id: str
    domain: str
    card_type: CardType
    front: str
    back: str
    tags: list[str] = Field(default_factory=list)

    # FSRS metrics
    stability: float = 0.0
    difficulty: float = 0.0
    repetition_count: int = 0
    due_date: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class ReviewInput(BaseModel):
    """User review/rating of a flashcard."""

    card_id: str
    rating: int  # 1-4: again, hard, good, easy


class DeckInfo(BaseModel):
    """Deck metadata for selection."""

    domain: str
    category: str
    glossary_name: str
    card_count: int
