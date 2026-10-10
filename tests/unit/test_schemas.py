from datetime import datetime

import pytest

from src.flashcards.domains.schemas import CardType, Flashcard, GlossaryEntry


def test_glossary_entry_minimal():
    """Test creating minimal glossary entry."""
    entry = GlossaryEntry(
        domain="insurance",
        category="property",
        title="Term",
        body="Definition",
    )

    assert entry.domain == "insurance"
    assert entry.title == "Term"
    assert entry.metadata == {}


def test_glossary_entry_with_metadata():
    """Test glossary entry with custom metadata."""
    entry = GlossaryEntry(
        domain="insurance",
        category="property",
        title="Deductible",
        body="Amount insured pays",
        metadata={"source": "NAIC", "year": 2024},
    )

    assert entry.metadata["source"] == "NAIC"


def test_flashcard_defaults():
    """Test flashcard with default FSRS values."""
    card = Flashcard(
        entry_id="test-1",
        domain="insurance",
        card_type=CardType.TERM_DEFINITION,
        front="Deductible",
        back="Amount insured pays",
    )

    assert card.stability == 0.0
    assert card.difficulty == 0.0
    assert card.repetition_count == 0
    assert isinstance(card.due_date, datetime)


def test_flashcard_tags():
    """Test flashcard tags default."""
    card = Flashcard(
        entry_id="test-1",
        domain="insurance",
        card_type=CardType.TERM_DEFINITION,
        front="Test",
        back="Definition",
        tags=["tag1", "tag2"],
    )

    assert card.tags == ["tag1", "tag2"]
    assert len(card.tags) == 2


def test_card_type_enum():
    """Test CardType enum values."""
    assert CardType.TERM_DEFINITION.value == "term_definition"
    assert CardType.CLOZE_DELETION.value == "cloze_deletion"
    assert CardType.QUOTE_ATTRIBUTION.value == "quote_attribution"
