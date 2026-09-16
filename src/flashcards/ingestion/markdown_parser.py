"""Parser for Markdown-formatted glossaries."""

import re
import uuid

from ..domains.schemas import GlossaryEntry
from .base import BaseGlossaryParser


class MarkdownGlossaryParser(BaseGlossaryParser):
    """Parser for Markdown glossaries.

    Supports two formats:

    **Format 1: Definition List**
    ```
    # Domain Name

    ## term 1
    Definition of term 1. Can be multiple paragraphs.

    Additional context or examples.

    ## term 2
    Definition of term 2.
    ```

    **Format 2: Two-column table**
    ```
    | Term | Definition |
    |------|------------|
    | term 1 | Definition of term 1 |
    | term 2 | Definition of term 2 |
    ```
    """

    def parse(self, content: str, domain: str, category: str) -> list[GlossaryEntry]:
        """Parse Markdown content into glossary entries.

        Tries definition list format first, then falls back to table format.
        """
        entries = []

        # Try definition list format (## Title + body)
        if "##" in content:
            entries = self._parse_definition_list(content, domain, category)

        # Try table format if no entries found
        if not entries and "|" in content:
            entries = self._parse_table_format(content, domain, category)

        return entries

    def _parse_definition_list(
        self, content: str, domain: str, category: str
    ) -> list[GlossaryEntry]:
        """Parse ## Title + body definition list format."""
        entries = []
        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Look for ## Title lines
            if line.startswith("## "):
                title = line[3:].strip()
                body_lines = []
                i += 1

                # Collect body until next ## or end
                while i < len(lines):
                    if lines[i].strip().startswith("## "):
                        break
                    if lines[i].strip() and not lines[i].startswith("#"):
                        body_lines.append(lines[i])
                    i += 1

                body = "\n".join(body_lines).strip()
                if title and body:
                    entry = GlossaryEntry(
                        id=str(uuid.uuid4()),
                        domain=domain,
                        category=category,
                        title=title,
                        body=body,
                        metadata={"format": "markdown_definition_list"},
                    )
                    entries.append(entry)
            else:
                i += 1

        return entries

    def _parse_table_format(
        self, content: str, domain: str, category: str
    ) -> list[GlossaryEntry]:
        """Parse Markdown table format (| Term | Definition |)."""
        entries = []
        lines = content.split("\n")

        # Find table start (line with |)
        table_start = None
        for i, line in enumerate(lines):
            if "|" in line and any(c in lines[i + 1] if i + 1 < len(lines) else False
                                    for c in ["-", ":|"]):
                table_start = i
                break

        if table_start is None:
            return entries

        # Parse table rows
        i = table_start
        # Skip header and separator
        if i + 1 < len(lines):
            i += 2

        while i < len(lines):
            line = lines[i].strip()
            if not line or not line.startswith("|"):
                break

            # Extract cells from |cell1|cell2|...| format
            cells = [cell.strip() for cell in line.split("|")[1:-1]]

            if len(cells) >= 2:
                title = cells[0]
                body = cells[1]
                if title and body:
                    entry = GlossaryEntry(
                        id=str(uuid.uuid4()),
                        domain=domain,
                        category=category,
                        title=title,
                        body=body,
                        metadata={"format": "markdown_table"},
                    )
                    entries.append(entry)

            i += 1

        return entries
