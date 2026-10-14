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

from .domains.schemas import GlossaryEntry
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
    """One subdeck in a composite: the tags it shows, and the version and mask those tags produced.

    `version` and `mask` are None in an authored file until `composite build` fills them in.
    """

    deck: str
    include_tags: frozenset[str]
    version: str | None = None
    mask: tuple[int, ...] | None = None


@dataclass(frozen=True)
class CompositeDeck:
    """A presentation: its subdecks in the order they are shown, each with its own slide selection."""

    name: str
    subdecks: tuple[SubdeckPin, ...]
    extra_slides: tuple[str, ...] = field(default_factory=tuple)


def pin_composite(composite: CompositeDeck, decks: dict[str, AtomicDeck], taxonomy: Taxonomy) -> CompositeDeck:
    """Return the composite with each subdeck's version and mask computed from its include_tags.

    Inclusion and order come from the definition and are kept as written. A missing or repeated subdeck, or one
    whose tags match no slide, is an error, so a definition cannot quietly present less than it lists.

    Raises:
        ValueError: On a missing or repeated subdeck, or a subdeck whose tags match no slide.
    """
    seen: set[str] = set()
    pinned: list[SubdeckPin] = []
    for sub in composite.subdecks:
        if sub.deck in seen:
            raise ValueError(f"{composite.name}: subdeck {sub.deck!r} is listed more than once")
        seen.add(sub.deck)
        if sub.deck not in decks:
            raise ValueError(f"{composite.name}: subdeck {sub.deck!r} does not exist")
        deck = decks[sub.deck]
        wanted = {taxonomy.resolve(tag) for tag in sub.include_tags}
        mask = tuple(1 if slide.tags & wanted else 0 for slide in deck.slides)
        if not any(mask):
            raise ValueError(f"{composite.name}: {sub.deck!r} has no slide tagged {sorted(sub.include_tags)}")
        pinned.append(SubdeckPin(deck=sub.deck, include_tags=sub.include_tags, version=deck.version, mask=mask))
    return CompositeDeck(name=composite.name, subdecks=tuple(pinned), extra_slides=composite.extra_slides)


def present(composite: CompositeDeck, decks: dict[str, AtomicDeck]) -> list[Slide]:
    """The slides a presentation shows, in subdeck order then slide order.

    Raises:
        PinError: If a subdeck is missing, its version has changed, or a mask does not cover
            its slides.
    """
    shown: list[Slide] = []
    for pin in composite.subdecks:
        if pin.version is None or pin.mask is None:
            raise PinError(f"{composite.name}: {pin.deck} is not built; run `flashcards composite build`")
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
    subdecks = []
    for pin in composite.subdecks:
        entry: dict = {"deck": pin.deck, "include_tags": sorted(pin.include_tags)}
        if pin.version is not None:
            entry["version"] = pin.version
        if pin.mask is not None:
            entry["mask"] = list(pin.mask)
        subdecks.append(entry)
    return {"name": composite.name, "subdecks": subdecks, "extra_slides": list(composite.extra_slides)}


def composite_from_dict(data: dict) -> CompositeDeck:
    if "include_tags" in data:
        raise ValueError(f"{data['name']}: include_tags now belongs to each subdeck; move it under subdecks")
    return CompositeDeck(
        name=data["name"],
        subdecks=tuple(
            SubdeckPin(
                deck=s["deck"],
                include_tags=frozenset(s["include_tags"]),
                version=s.get("version"),
                mask=tuple(s["mask"]) if "mask" in s else None,
            )
            for s in data["subdecks"]
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


def composite_entries(name: str, slides: list[Slide]) -> list[GlossaryEntry]:
    """Presented slides as glossary entries under the composite's own domain, so cards are generated and studied
    the same way as an atomic deck's."""
    return [
        GlossaryEntry(
            id=slide.id,
            domain=name,
            category="composite",
            title=slide.title,
            body=slide.body,
            metadata={"tags": sorted(slide.tags)},
        )
        for slide in slides
    ]


def composite_card_count(composite: CompositeDeck) -> int:
    """Number of slides the composite presents, read from its masks."""
    return sum(sum(pin.mask or ()) for pin in composite.subdecks)
