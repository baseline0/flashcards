from abc import ABC, abstractmethod

from ..domains.schemas import GlossaryEntry


class BaseGlossaryParser(ABC):
    """Base class for glossary parsers."""

    @abstractmethod
    def parse(self, content: str, domain: str, category: str) -> list[GlossaryEntry]:
        """Parse raw content into glossary entries."""
        pass
