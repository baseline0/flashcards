import json
import uuid

from flashcards.domains.schemas import GlossaryEntry
from flashcards.taxonomy import Taxonomy

from .base import BaseGlossaryParser


class JSONGlossaryParser(BaseGlossaryParser):
    """Parser for JSON glossaries; each entry's tags resolve to canonical taxonomy tags."""

    def __init__(self, taxonomy: Taxonomy):
        self._taxonomy = taxonomy

    def parse(self, content: str, domain: str, category: str) -> list[GlossaryEntry]:
        """Parse JSON content into glossary entries.

        Expects JSON array of objects with 'title' and 'body' keys. A tag that matches no canonical tag or
        synonym raises UnknownTagError, so a deck cannot enter the database with a raw tag.
        """
        data = json.loads(content)
        if not isinstance(data, list):
            data = [data]

        entries = []
        for item in data:
            metadata = dict(item.get("metadata", {}))
            if "tags" in metadata:
                metadata["tags"] = [self._taxonomy.resolve(tag) for tag in metadata["tags"]]
            entry = GlossaryEntry(
                id=str(uuid.uuid4()),
                domain=domain,
                category=category,
                title=item.get("title", ""),
                body=item.get("body", ""),
                metadata=metadata,
            )
            entries.append(entry)
        return entries
