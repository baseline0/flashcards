"""Atomic decks, pinned composite decks, and the presentation they expand to.

An atomic deck is one glossary file. Its slides are ordered, each has a stable ID derived
from the deck name and slide title, and its version is a content hash, so a change to any
slide is a new version.

A composite deck lists subdecks. Each subdeck is pinned to a version and carries a binary
mask with one flag per slide index of that version: 1 shows the slide in the presentation,
0 hides it. Composite decks are built from a tag query, which is resolved once and recorded
as pins, so later changes to a subdeck are visible in review rather than silently applied.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .taxonomy import Taxonomy

SLIDE_NAMESPACE = uuid.UUID("6b1f2a4e-2c2d-4f4e-9a8f-5a6f1d0c7b11")


class PinError(ValueError):
    """A composite refers to a subdeck version or mask that does not match the subdeck."""


@dataclass(frozen=True)
class Slide:
    id: str
    title: str
    body: str
    tags: frozenset[str]


@dataclass(frozen=True)
class AtomicDeck:
    name: str
    version: str
    slides: tuple[Slide, ...]


def slide_id(deck: str, title: str) -> str:
    """Stable identifier: the same deck and title always give the same ID."""
    return str(uuid.uuid5(SLIDE_NAMESPACE, f"{deck}\x1f{title}"))


def deck_version(slides: tuple[Slide, ...]) -> str:
    """Content hash over slide IDs, titles, bodies and tags, in order.

    Any change gives a new version.
    """
    digest = hashlib.sha256()
    for slide in slides:
        record = {
            "id": slide.id,
            "title": slide.title,
            "body": slide.body,
            "tags": sorted(slide.tags),
        }
        digest.update(json.dumps(record, sort_keys=True).encode())
    return "v" + digest.hexdigest()[:12]


def load_atomic_deck(name: str, path: Path, taxonomy: Taxonomy) -> AtomicDeck:
    """Read a glossary file as an atomic deck, normalizing every tag through the taxonomy.

    Raises:
        ValueError: If two slides share a title, since their IDs would collide.
        UnknownTagError: If a tag is not in the taxonomy.
    """
    entries = json.loads(path.read_text())
    titles = [entry["title"] for entry in entries]
    if len(titles) != len(set(titles)):
        raise ValueError(f"{name}: slide titles must be unique")
    slides = tuple(
        Slide(
            id=slide_id(name, entry["title"]),
            title=entry["title"],
            body=entry.get("body", ""),
            tags=frozenset(taxonomy.resolve(t) for t in entry.get("metadata", {}).get("tags", [])),
        )
        for entry in entries
    )
    return AtomicDeck(name=name, version=deck_version(slides), slides=slides)


@dataclass(frozen=True)
class SubdeckPin:
    deck: str
    version: str
    mask: tuple[int, ...]


@dataclass(frozen=True)
class CompositeDeck:
    name: str
    include_tags: frozenset[str]
    subdecks: tuple[SubdeckPin, ...]
    extra_slides: tuple[str, ...] = field(default_factory=tuple)


def build_composite(
    name: str,
    include_tags: set[str],
    decks: dict[str, AtomicDeck],
    taxonomy: Taxonomy,
) -> CompositeDeck:
    """Pin every subdeck with at least one matching slide, masking exactly the matching slides.

    Args:
        name: Composite deck name.
        include_tags: Canonical tags; a slide matches when it carries any of them.
        decks: Atomic decks by name.
        taxonomy: Used to normalize the include tags.
    """
    wanted = {taxonomy.resolve(tag) for tag in include_tags}
    pins = []
    for deck_name in sorted(decks):
        deck = decks[deck_name]
        mask = tuple(1 if slide.tags & wanted else 0 for slide in deck.slides)
        if any(mask):
            pins.append(SubdeckPin(deck=deck_name, version=deck.version, mask=mask))
    return CompositeDeck(name=name, include_tags=frozenset(wanted), subdecks=tuple(pins))


def present(composite: CompositeDeck, decks: dict[str, AtomicDeck]) -> list[Slide]:
    """The slides a presentation shows, in subdeck order then slide order.

    Raises:
        PinError: If a subdeck is missing, its version has changed, or a mask does not cover
            its slides.
    """
    shown: list[Slide] = []
    for pin in composite.subdecks:
        if pin.deck not in decks:
            raise PinError(f"{composite.name}: subdeck {pin.deck!r} is missing")
        deck = decks[pin.deck]
        if deck.version != pin.version:
            raise PinError(
                f"{composite.name}: {pin.deck} is pinned to {pin.version} "
                f"but is now {deck.version}; rebuild the composite"
            )
        if len(pin.mask) != len(deck.slides):
            raise PinError(
                f"{composite.name}: mask for {pin.deck} has {len(pin.mask)} flags for {len(deck.slides)} slides"
            )
        shown.extend(slide for slide, keep in zip(deck.slides, pin.mask, strict=True) if keep)
    return shown


def composite_to_dict(composite: CompositeDeck) -> dict:
    return {
        "name": composite.name,
        "include_tags": sorted(composite.include_tags),
        "subdecks": [{"deck": pin.deck, "version": pin.version, "mask": list(pin.mask)} for pin in composite.subdecks],
        "extra_slides": list(composite.extra_slides),
    }


def composite_from_dict(data: dict) -> CompositeDeck:
    return CompositeDeck(
        name=data["name"],
        include_tags=frozenset(data.get("include_tags", [])),
        subdecks=tuple(
            SubdeckPin(deck=s["deck"], version=s["version"], mask=tuple(s["mask"])) for s in data["subdecks"]
        ),
        extra_slides=tuple(data.get("extra_slides", [])),
    )


def write_composite(composite: CompositeDeck, path: Path) -> None:
    path.write_text(yaml.safe_dump(composite_to_dict(composite), sort_keys=False))


def read_composite(path: Path) -> CompositeDeck:
    return composite_from_dict(yaml.safe_load(path.read_text()))


def load_all_decks(glossaries_root: Path, taxonomy: Taxonomy) -> dict[str, AtomicDeck]:
    """Load every glossary JSON under the root as an atomic deck, named by its relative path."""
    decks = {}
    for path in sorted(glossaries_root.rglob("*.json")):
        name = path.relative_to(glossaries_root).with_suffix("").as_posix()
        decks[name] = load_atomic_deck(name, path, taxonomy)
    return decks


def check_name_collisions(atomic_names: set[str], composite_names: set[str]) -> None:
    """Forbid a composite sharing a name with an atomic deck, comparing the final path component.

    Raises:
        ValueError: Listing every collision, so the fix is visible in one run.
    """
    atomic_basenames = {name.rsplit("/", 1)[-1] for name in atomic_names}
    collisions = sorted(composite_names & atomic_basenames)
    if collisions:
        raise ValueError(f"composite names collide with atomic deck names: {collisions}")


def load_composites(composite_root: Path) -> dict[str, CompositeDeck]:
    """Read every composite under the root. A file must be named after its composite.

    Raises:
        ValueError: If a file's name does not match the composite inside it.
    """
    composites: dict[str, CompositeDeck] = {}
    for path in sorted(composite_root.glob("*.deck.yaml")):
        composite = read_composite(path)
        if path.name != f"{composite.name}.deck.yaml":
            raise ValueError(f"{path.name} must be named {composite.name}.deck.yaml")
        composites[composite.name] = composite
    return composites


def composite_card_count(composite: CompositeDeck) -> int:
    """Number of slides the composite presents, read from its masks."""
    return sum(sum(pin.mask) for pin in composite.subdecks)
