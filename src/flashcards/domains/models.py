"""ORM models for raw glossary entries and generated flashcards.

Columns use SQLAlchemy 2.0 `Mapped[...]` annotations so type checkers see plain Python values. Nullability
matches the database as it already exists: a column that was nullable stays nullable here.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from flashcards.core.database import Base


class GlossaryEntryModel(Base):
    """ORM model for raw glossary entries."""

    __tablename__ = "glossary_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    domain: Mapped[str] = mapped_column(String, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[str] = mapped_column(String, nullable=True, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=datetime.now)


class FlashcardModel(Base):
    """ORM model for generated flashcards."""

    __tablename__ = "flashcards"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    entry_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String, nullable=False, index=True)
    card_type: Mapped[str] = mapped_column(String, nullable=False)
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    tags_json: Mapped[str] = mapped_column(String, nullable=True, default="[]")

    # FSRS metrics
    stability: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    difficulty: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    repetition_count: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=datetime.now, index=True)
    fsrs_card: Mapped[str | None] = mapped_column(Text, nullable=True)  # py-fsrs Card as JSON; NULL before a review

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=datetime.now)
