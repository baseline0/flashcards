"""Spaced-repetition scheduling with py-fsrs.

A flashcard keeps its full FSRS state as JSON in `fsrs_card`, so the scheduler resumes from the real
learning/review state rather than rebuilding a card from its counters. Due dates are stored as naive UTC,
matching the rest of the database.
"""

from datetime import UTC, datetime
from typing import Protocol

from fsrs import Card, Rating, Scheduler


class ReviewableCard(Protocol):
    """The flashcard fields a review reads and writes."""

    fsrs_card: str | None
    due_date: datetime
    stability: float
    difficulty: float
    repetition_count: int


class FSRSEngine:
    """Applies a rating to a flashcard in place."""

    def __init__(self) -> None:
        self._scheduler = Scheduler()

    def review(self, flashcard: ReviewableCard, rating: Rating, now: datetime | None = None) -> None:
        """Update the card's FSRS state, due date, stability, difficulty and review count for one rating."""
        when = now or datetime.now(UTC)
        if when.tzinfo is None:  # the database stores naive UTC; py-fsrs requires an aware UTC time
            when = when.replace(tzinfo=UTC)
        card = Card.from_json(flashcard.fsrs_card) if flashcard.fsrs_card else Card()
        card, _log = self._scheduler.review_card(card, rating, when)
        flashcard.fsrs_card = card.to_json()
        flashcard.due_date = card.due.astimezone(UTC).replace(tzinfo=None)
        flashcard.stability = card.stability or 0.0
        flashcard.difficulty = card.difficulty or 0.0
        flashcard.repetition_count = (flashcard.repetition_count or 0) + 1
