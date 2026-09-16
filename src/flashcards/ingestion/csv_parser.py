"""Parser for CSV-formatted glossaries."""

import csv
import io
import uuid

from ..domains.schemas import GlossaryEntry
from .base import BaseGlossaryParser


class CSVGlossaryParser(BaseGlossaryParser):
    """Parser for CSV glossaries.

    Expected CSV format (with headers):
    - term: The glossary term/title
    - definition: The term definition/body
    - category: (optional) Category for the term
    - difficulty: (optional) Difficulty level (beginner/intermediate/advanced)
    - source: (optional) Source reference
    """

    def parse(self, content: str, domain: str, category: str) -> list[GlossaryEntry]:
        """Parse CSV content into glossary entries.

        CSV must have 'term' and 'definition' columns at minimum.
        """
        entries = []
        reader = csv.DictReader(io.StringIO(content))

        if not reader.fieldnames or "term" not in reader.fieldnames:
            raise ValueError("CSV must have 'term' column")
        if "definition" not in reader.fieldnames:
            raise ValueError("CSV must have 'definition' column")

        for row in reader:
            metadata = {}
            if "difficulty" in row and row["difficulty"]:
                metadata["difficulty"] = row["difficulty"]
            if "source" in row and row["source"]:
                metadata["source"] = row["source"]

            entry = GlossaryEntry(
                id=str(uuid.uuid4()),
                domain=domain,
                category=row.get("category", category),
                title=row["term"].strip(),
                body=row["definition"].strip(),
                metadata=metadata,
            )
            entries.append(entry)

        return entries
