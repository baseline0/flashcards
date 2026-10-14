"""Spaced-repetition scheduling with py-fsrs.

`FSRSEngine.review` is a pure function of the card's stored FSRS state, the rating, and the time. It returns the new
state for the caller to store. The FSRS state is kept as JSON so the next interval grows from the last review.
Due dates are naive UTC, matching the database.
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from fsrs import Card, Rating, Scheduler


@dataclass(frozen=True)
class Scheduled:
    """The card state after one review."""

    fsrs_card: str
    due_date: datetime
    stability: float
    difficulty: float


class FSRSEngine:
    """Schedules a review of a card's stored state."""

    def __init__(self) -> None:
        self._scheduler = Scheduler()

    def review(self, fsrs_card: str | None, rating: Rating, now: datetime | None = None) -> Scheduled:
        """Schedule a review. A card with no stored state is treated as new."""
        when = now or datetime.now(UTC)
        if when.tzinfo is None:  # the database stores naive UTC; py-fsrs requires an aware UTC time
            when = when.replace(tzinfo=UTC)
        card = Card.from_json(fsrs_card) if fsrs_card else Card()
        card, _log = self._scheduler.review_card(card, rating, when)
        return Scheduled(
            fsrs_card=card.to_json(),
            due_date=card.due.astimezone(UTC).replace(tzinfo=None),
            stability=card.stability or 0.0,
            difficulty=card.difficulty or 0.0,
        )
