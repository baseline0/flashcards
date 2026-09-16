"""Parser for YAML-formatted glossaries."""

import re
import uuid
from typing import Any

from ..domains.schemas import GlossaryEntry
from .base import BaseGlossaryParser


class YAMLGlossaryParser(BaseGlossaryParser):
    """Parser for YAML glossaries.

    Supports YAML list of glossary entries with title/body or term/definition.

    Example:
    ```yaml
    glossary:
      - title: "Term 1"
        body: "Definition of term 1"
        difficulty: "beginner"
      - term: "Term 2"
        definition: "Definition of term 2"
        difficulty: "intermediate"
    ```

    Or flat list:
    ```yaml
    - title: "Term 1"
      body: "Definition"
    - title: "Term 2"
      body: "Definition"
    ```
    """

    def parse(self, content: str, domain: str, category: str) -> list[GlossaryEntry]:
        """Parse YAML content into glossary entries.

        Uses basic YAML parsing (no external library required).
        """
        try:
            # Try to import pyyaml if available
            import yaml
            data = yaml.safe_load(content)
        except ImportError:
            # Fallback: parse simple YAML manually
            data = self._parse_simple_yaml(content)

        return self._extract_entries(data, domain, category)

    def _parse_simple_yaml(self, content: str) -> list[dict[str, Any]]:
        """Simple YAML parser for basic structures (no pyyaml dependency)."""
        entries = []
        lines = content.split("\n")
        current_entry: dict[str, Any] = {}
        current_key = None
        current_value_lines = []

        for line in lines:
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith("#"):
                continue

            # Detect list item (- key: value)
            if line.startswith("- "):
                if current_entry:
                    entries.append(current_entry)
                current_entry = {}
                line = line[2:].lstrip()

            # Parse key: value
            if ": " in line:
                if current_key and current_value_lines:
                    current_entry[current_key] = " ".join(current_value_lines).strip()
                    current_value_lines = []

                key, value = line.split(": ", 1)
                current_key = key.strip()
                # Remove quotes if present
                value = value.strip().strip('"\'')
                current_value_lines = [value] if value else []
            elif line.startswith("  ") and current_key:
                # Continuation of multiline value
                current_value_lines.append(line.strip())

        # Add last entry
        if current_key and current_value_lines:
            current_entry[current_key] = " ".join(current_value_lines).strip()
        if current_entry:
            entries.append(current_entry)

        return entries

    def _extract_entries(
        self, data: Any, domain: str, category: str
    ) -> list[GlossaryEntry]:
        """Extract GlossaryEntry objects from parsed YAML data."""
        entries = []

        # Handle dict with 'glossary' key
        if isinstance(data, dict) and "glossary" in data:
            items = data["glossary"]
        # Handle dict with 'entries' key
        elif isinstance(data, dict) and "entries" in data:
            items = data["entries"]
        # Handle list directly
        elif isinstance(data, list):
            items = data
        else:
            return entries

        # Process items
        if not isinstance(items, list):
            items = [items]

        for item in items:
            if not isinstance(item, dict):
                continue

            # Support both title/body and term/definition keys
            title = item.get("title") or item.get("term", "")
            body = item.get("body") or item.get("definition", "")

            if title and body:
                metadata = {}
                if "difficulty" in item:
                    metadata["difficulty"] = item["difficulty"]
                if "source" in item:
                    metadata["source"] = item["source"]
                if "category" in item:
                    category = item["category"]

                entry = GlossaryEntry(
                    id=str(uuid.uuid4()),
                    domain=domain,
                    category=category,
                    title=title,
                    body=body,
                    metadata={**metadata, "format": "yaml"},
                )
                entries.append(entry)

        return entries
