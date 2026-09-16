from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from ..core.database import Base


class GlossaryEntryModel(Base):
    """ORM model for raw glossary entries."""

    __tablename__ = "glossary_entries"

    id = Column(String, primary_key=True)
    domain = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    metadata_json = Column(String, default="{}")
    created_at = Column(DateTime, default=datetime.now)


class FlashcardModel(Base):
    """ORM model for generated flashcards."""

    __tablename__ = "flashcards"

    id = Column(String, primary_key=True)
    entry_id = Column(String, nullable=False, index=True)
    domain = Column(String, nullable=False, index=True)
    card_type = Column(String, nullable=False)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    tags_json = Column(String, default="[]")

    # FSRS metrics
    stability = Column(Float, default=0.0)
    difficulty = Column(Float, default=0.0)
    repetition_count = Column(Integer, default=0)
    due_date = Column(DateTime, default=datetime.now, index=True)

    created_at = Column(DateTime, default=datetime.now)
