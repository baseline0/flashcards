from ..domains.schemas import CardType, Flashcard, GlossaryEntry
from .base import BaseCardGenerator


class TermDefinitionGenerator(BaseCardGenerator):
    """Generator for term ↔ definition cards (insurance, science, etc.)."""

    def generate(self, entry: GlossaryEntry) -> list[Flashcard]:
        """Create bidirectional term/definition cards."""
        cards = []

        # Card 1: Term → Definition
        cards.append(
            Flashcard(
                id=self._make_id(),
                entry_id=entry.id,
                domain=entry.domain,
                card_type=CardType.TERM_DEFINITION,
                front=entry.title,
                back=entry.body,
                tags=[entry.domain, entry.category],
            )
        )

        # Card 2: Definition → Term (reverse lookup)
        cards.append(
            Flashcard(
                id=self._make_id(),
                entry_id=entry.id,
                domain=entry.domain,
                card_type=CardType.TERM_DEFINITION,
                front=entry.body[:100] + ("..." if len(entry.body) > 100 else ""),
                back=entry.title,
                tags=[entry.domain, entry.category, "reverse"],
            )
        )

        return cards
