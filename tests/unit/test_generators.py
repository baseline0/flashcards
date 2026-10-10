import pytest

from src.flashcards.domains.schemas import CardType, GlossaryEntry
from src.flashcards.generators.term_def_generator import TermDefinitionGenerator


def test_term_def_generates_two_cards():
    """Test that term definition generator creates bidirectional cards."""
    generator = TermDefinitionGenerator()
    entry = GlossaryEntry(
        id="test-1",
        domain="insurance",
        category="property",
        title="Deductible",
        body="Amount insured pays out of pocket",
    )

    cards = generator.generate(entry)

    assert len(cards) == 2
    assert all(card.card_type == CardType.TERM_DEFINITION for card in cards)


def test_term_def_creates_forward_and_reverse():
    """Test forward (term→def) and reverse (def→term) cards."""
    generator = TermDefinitionGenerator()
    entry = GlossaryEntry(
        id="test-1",
        domain="insurance",
        category="property",
        title="Premium",
        body="Amount paid to insurer for coverage",
    )

    cards = generator.generate(entry)

    # First card: term → definition
    assert cards[0].front == "Premium"
    assert cards[0].back == "Amount paid to insurer for coverage"

    # Second card: definition (snippet) → term
    assert "Amount paid" in cards[1].front
    assert cards[1].back == "Premium"
    assert "reverse" in cards[1].tags


def test_cards_inherit_tags():
    """Test that generated cards inherit domain and category tags."""
    generator = TermDefinitionGenerator()
    entry = GlossaryEntry(
        id="test-1",
        domain="insurance",
        category="property",
        title="Claim",
        body="Request for payment",
    )

    cards = generator.generate(entry)

    for card in cards:
        assert "insurance" in card.tags
        assert "property" in card.tags
