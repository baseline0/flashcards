"""The server loads a composite from its presented slides, keyed by the composite's name.

Happy path: a composite loads, its cards study under its own name, and the listing shows it as a composite.
Unhappy paths: an unknown composite is 404; a composite whose subdeck changed after pinning is 422 and stores nothing.
"""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from flashcards import composite
from flashcards.core.database import Base, get_session
from flashcards.domains import models  # noqa: F401  (registers FlashcardModel on Base)
from flashcards.server.app import app
from flashcards.server.routes import api as api_routes
from flashcards.taxonomy import load_taxonomy


@pytest.fixture
def client(tmp_path: Path, monkeypatch):
    data = tmp_path / "data"
    glossaries = data / "raw_glossaries"
    (glossaries / "topic").mkdir(parents=True)
    (data / "taxonomy.yaml").write_text("tags:\n  alpha:\n    description: x\n")
    deck = glossaries / "topic" / "alpha.json"
    deck.write_text(json.dumps([{"title": "One", "body": "a", "metadata": {"tags": ["alpha"]}}]))

    taxonomy = load_taxonomy(data / "taxonomy.yaml")
    decks = composite.load_all_decks(glossaries, taxonomy)
    pinned = composite.build_composite("track", {"alpha"}, decks, taxonomy)
    composites = data / "composite_decks"
    composites.mkdir()
    composite.write_composite(pinned, composites / "track.deck.yaml")

    monkeypatch.setattr(
        api_routes,
        "settings",
        SimpleNamespace(glossaries_path=glossaries, composite_decks_path=composites),
    )

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    def override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override
    yield TestClient(app), deck
    app.dependency_overrides.clear()


def test_composite_loads_and_studies_under_its_own_name(client):
    http, _ = client
    loaded = http.post(
        "/api/deck/load",
        params={"domain": "composite", "category": "composite", "glossary_name": "track", "kind": "composite"},
    )
    assert loaded.status_code == 200, loaded.text
    assert loaded.json()["card_count"] > 0

    study = http.get("/api/deck/study", params={"domain": "track", "shuffle": "false"})
    assert study.status_code == 200
    assert {card["domain"] for card in study.json()} == {"track"}


def test_composite_listing_names_the_deck_by_its_composite_name(client):
    http, _ = client
    decks = http.get("/api/decks").json()
    (track,) = [d for d in decks if d["kind"] == "composite"]
    assert track["domain"] == "track"
    assert track["glossary_name"] == "track"


def test_unknown_composite_is_not_found(client):
    http, _ = client
    response = http.post(
        "/api/deck/load",
        params={"domain": "composite", "category": "composite", "glossary_name": "missing", "kind": "composite"},
    )
    assert response.status_code == 404


def test_stale_pin_is_refused_and_stores_nothing(client):
    http, deck = client
    cards = json.loads(deck.read_text())
    cards[0]["body"] = "changed after pinning"
    deck.write_text(json.dumps(cards))

    response = http.post(
        "/api/deck/load",
        params={"domain": "composite", "category": "composite", "glossary_name": "track", "kind": "composite"},
    )
    assert response.status_code == 422
    assert http.get("/api/deck/study", params={"domain": "track", "shuffle": "false"}).json() == []
