import json

import pytest

from src.flashcards.ingestion.json_parser import JSONGlossaryParser


def test_parse_json_list():
    """Test parsing JSON array of glossary entries."""
    parser = JSONGlossaryParser()
    content = json.dumps(
        [
            {"title": "Term1", "body": "Definition1"},
            {"title": "Term2", "body": "Definition2", "metadata": {"source": "test"}},
        ]
    )

    entries = parser.parse(content, domain="test", category="test_cat")

    assert len(entries) == 2
    assert entries[0].title == "Term1"
    assert entries[0].domain == "test"
    assert entries[1].metadata["source"] == "test"


def test_parse_json_object():
    """Test parsing JSON object as single entry."""
    parser = JSONGlossaryParser()
    content = json.dumps({"title": "Single", "body": "Entry"})

    entries = parser.parse(content, domain="test", category="test_cat")

    assert len(entries) == 1
    assert entries[0].title == "Single"


def test_parse_generates_ids():
    """Test that parser generates unique IDs."""
    parser = JSONGlossaryParser()
    content = json.dumps([{"title": "A", "body": "B"}, {"title": "C", "body": "D"}])

    entries = parser.parse(content, "test", "test")

    assert entries[0].id is not None
    assert entries[1].id is not None
    assert entries[0].id != entries[1].id
