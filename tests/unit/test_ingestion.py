import json
from pathlib import Path

import pytest

from flashcards.ingestion.json_parser import JSONGlossaryParser
from flashcards.taxonomy import UnknownTagError, load_taxonomy


@pytest.fixture
def taxonomy(tmp_path: Path):
    path = tmp_path / "taxonomy.yaml"
    path.write_text("tags:\n  llm:\n    description: x\n  bert:\n    synonyms: [Bert Deck]\n")
    return load_taxonomy(path)


def test_parse_json_list(taxonomy):
    """Test parsing JSON array of glossary entries."""
    parser = JSONGlossaryParser(taxonomy)
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


def test_parse_json_object(taxonomy):
    """Test parsing JSON object as single entry."""
    parser = JSONGlossaryParser(taxonomy)
    content = json.dumps({"title": "Single", "body": "Entry"})

    entries = parser.parse(content, domain="test", category="test_cat")

    assert len(entries) == 1
    assert entries[0].title == "Single"


def test_parse_generates_ids(taxonomy):
    """Test that parser generates unique IDs."""
    parser = JSONGlossaryParser(taxonomy)
    content = json.dumps([{"title": "A", "body": "B"}, {"title": "C", "body": "D"}])

    entries = parser.parse(content, "test", "test")

    assert entries[0].id is not None
    assert entries[1].id is not None
    assert entries[0].id != entries[1].id


def test_parse_resolves_tags_to_canonical_names(taxonomy):
    """Raw tags such as 'LLM' and 'Bert Deck' are stored as canonical tags."""
    parser = JSONGlossaryParser(taxonomy)
    content = json.dumps([{"title": "T", "body": "B", "metadata": {"tags": ["LLM", "Bert Deck"]}}])

    (entry,) = parser.parse(content, "test", "test")

    assert entry.metadata["tags"] == ["llm", "bert"]


def test_parse_rejects_an_unknown_tag(taxonomy):
    """A tag the taxonomy does not know fails loudly instead of entering the database."""
    parser = JSONGlossaryParser(taxonomy)
    content = json.dumps([{"title": "T", "body": "B", "metadata": {"tags": ["Unlisted"]}}])

    with pytest.raises(UnknownTagError):
        parser.parse(content, "test", "test")
