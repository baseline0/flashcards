"""Canonical topic tags for flashcard decks.

`data/taxonomy.yaml` is the source of truth. Every raw tag found in a glossary resolves to
exactly one canonical tag, matched case-insensitively against canonical names and synonyms.
An unknown raw tag is an error, so a new topic must be added to the taxonomy before a deck
can use it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


class UnknownTagError(ValueError):
    """A raw tag matches no canonical tag or synonym."""


@dataclass(frozen=True)
class Taxonomy:
    """Canonical tags and a case-insensitive lookup from any accepted spelling."""

    canonical: frozenset[str]
    _lookup: dict[str, str] = field(repr=False)

    def resolve(self, raw: str) -> str:
        """Return the canonical tag for a raw tag, or raise UnknownTagError."""
        key = raw.strip().lower()
        if key not in self._lookup:
            raise UnknownTagError(
                f"unknown tag {raw!r}: add it to data/taxonomy.yaml or fix the spelling"
            )
        return self._lookup[key]


def load_taxonomy(path: Path) -> Taxonomy:
    """Load and validate the taxonomy file.

    Raises:
        ValueError: If a canonical name or synonym appears under more than one tag.
    """
    tags = yaml.safe_load(path.read_text())["tags"]
    lookup: dict[str, str] = {}
    for name, entry in tags.items():
        if name != name.lower() or " " in name:
            raise ValueError(f"canonical tag {name!r} must be lowercase kebab-case")
        for spelling in [name, *(entry.get("synonyms") or [])]:
            key = spelling.strip().lower()
            if key in lookup:
                raise ValueError(f"{spelling!r} is claimed by both {lookup[key]!r} and {name!r}")
            lookup[key] = name
    return Taxonomy(canonical=frozenset(tags), _lookup=lookup)
