"""POST /api/card/review reschedules the card with FSRS and refuses bad input.

Happy path: a good review stores FSRS state and returns the new due date.
Unhappy paths: an unknown card is 404; a rating outside 1 to 4 is 422 and changes nothing.
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from flashcards.core.database import Base, get_session
from flashcards.domains.models import FlashcardModel
from flashcards.server.app import app


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    with session_factory() as seed:
        seed.add(
            FlashcardModel(
                id="card-1",
                entry_id="entry-1",
                domain="d",
                card_type="term",
                front="f",
                back="b",
                repetition_count=0,
                due_date=datetime(2026, 1, 1),
            )
        )
        seed.commit()

    def override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override
    yield TestClient(app), session_factory
    app.dependency_overrides.clear()


def test_good_review_stores_fsrs_state_and_returns_the_due_date(client):
    http, session_factory = client

    response = http.post("/api/card/review", json={"card_id": "card-1", "rating": 3})

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "reviewed"
    assert body["repetition_count"] == 1
    with session_factory() as check:
        stored = check.get(FlashcardModel, "card-1")
        assert stored.fsrs_card is not None
        assert stored.due_date > datetime(2026, 1, 1)


def test_unknown_card_is_not_found(client):
    http, _ = client
    response = http.post("/api/card/review", json={"card_id": "missing", "rating": 3})
    assert response.status_code == 404


@pytest.mark.parametrize("rating", [0, 5])
def test_rating_outside_one_to_four_is_refused_and_changes_nothing(client, rating):
    http, session_factory = client

    response = http.post("/api/card/review", json={"card_id": "card-1", "rating": rating})

    assert response.status_code == 422
    with session_factory() as check:
        stored = check.get(FlashcardModel, "card-1")
        assert stored.fsrs_card is None
        assert stored.repetition_count == 0
