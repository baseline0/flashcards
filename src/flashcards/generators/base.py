from abc import ABC, abstractmethod
import uuid

from ..domains.schemas import CardType, Flashcard, GlossaryEntry


class BaseCardGenerator(ABC):
    """Base class for card generators."""

    @abstractmethod
    def generate(self, entry: GlossaryEntry) -> list[Flashcard]:
        """Transform a glossary entry into one or more flashcards."""
        pass

    def _make_id(self) -> str:
        """Generate unique card ID."""
        return str(uuid.uuid4())
