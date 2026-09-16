import json
import uuid

from ..domains.schemas import GlossaryEntry
from .base import BaseGlossaryParser


class JSONGlossaryParser(BaseGlossaryParser):
    """Parser for JSON glossaries."""

    def parse(self, content: str, domain: str, category: str) -> list[GlossaryEntry]:
        """Parse JSON content into glossary entries.

        Expects JSON array of objects with 'title' and 'body' keys.
        """
        data = json.loads(content)
        if not isinstance(data, list):
            data = [data]

        entries = []
        for item in data:
            entry = GlossaryEntry(
                id=str(uuid.uuid4()),
                domain=domain,
                category=category,
                title=item.get("title", ""),
                body=item.get("body", ""),
                metadata=item.get("metadata", {}),
            )
            entries.append(entry)
        return entries
