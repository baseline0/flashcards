"""FSRS reviews schedule from the card's own state, so each interval grows from the last review.

Happy path: a first review stores FSRS state and a future due date; a second good review schedules later than the
first; an easy rating schedules later than an again rating from the same starting point.
Unhappy path: a card with no stored state is treated as new, not as an error.
"""

from datetime import UTC, datetime

from fsrs import Card, Rating, State

from flashcards.srs.fsrs_engine import FSRSEngine

NOW = datetime(2026, 10, 14, 12, 0, tzinfo=UTC)


def test_first_review_stores_state_and_schedules_in_the_future():
    result = FSRSEngine().review(None, Rating.Good, NOW)

    stored = Card.from_json(result.fsrs_card)
    assert stored.state == State.Learning
    assert stored.last_review is not None
    assert result.due_date > NOW.replace(tzinfo=None)
    assert result.stability > 0


def test_a_second_good_review_schedules_later_than_the_first():
    engine = FSRSEngine()
    first = engine.review(None, Rating.Good, NOW)

    second = engine.review(first.fsrs_card, Rating.Good, first.due_date)

    assert second.due_date > first.due_date


def test_easy_schedules_later_than_again_from_the_same_start():
    engine = FSRSEngine()

    again = engine.review(None, Rating.Again, NOW)
    easy = engine.review(None, Rating.Easy, NOW)

    assert easy.due_date > again.due_date


def test_a_card_without_stored_state_is_treated_as_new():
    result = FSRSEngine().review(None, Rating.Good, NOW)

    assert Card.from_json(result.fsrs_card).state == State.Learning
