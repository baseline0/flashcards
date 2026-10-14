"""FSRS reviews keep the card's own state, so the next interval grows from the last review.

Happy path: a first review stores FSRS state and a future due date; a second good review schedules later than the
first; an easy rating schedules later than an again rating from the same starting point.
Unhappy path: a card with no stored state is treated as new, not as an error.
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from fsrs import Card, Rating, State

from flashcards.srs.fsrs_engine import FSRSEngine


@dataclass
class FakeFlashcard:
    fsrs_card: str | None
    due_date: datetime
    stability: float
    difficulty: float
    repetition_count: int


NOW = datetime(2026, 10, 14, 12, 0, tzinfo=UTC)


def _new_flashcard() -> FakeFlashcard:
    return FakeFlashcard(
        fsrs_card=None, due_date=NOW.replace(tzinfo=None), stability=0.0, difficulty=0.0, repetition_count=0
    )


def test_first_review_stores_state_and_schedules_in_the_future():
    card = _new_flashcard()

    FSRSEngine().review(card, Rating.Good, NOW)

    assert card.fsrs_card is not None
    stored = Card.from_json(card.fsrs_card)
    assert stored.state == State.Learning
    assert stored.last_review is not None
    assert card.repetition_count == 1
    assert card.due_date > NOW.replace(tzinfo=None)
    assert card.stability > 0


def test_a_second_good_review_schedules_later_than_the_first():
    engine = FSRSEngine()
    card = _new_flashcard()
    engine.review(card, Rating.Good, NOW)
    first_due = card.due_date

    engine.review(card, Rating.Good, card.due_date)

    assert card.due_date > first_due
    assert card.repetition_count == 2


def test_easy_schedules_later_than_again_from_the_same_start():
    engine = FSRSEngine()
    again, easy = _new_flashcard(), _new_flashcard()
    engine.review(again, Rating.Again, NOW)
    engine.review(easy, Rating.Easy, NOW)

    assert easy.due_date > again.due_date


def test_a_card_without_stored_state_is_treated_as_new():
    card = _new_flashcard()
    card.repetition_count = 0
    card.fsrs_card = None

    FSRSEngine().review(card, Rating.Good, NOW)

    assert card.repetition_count == 1
