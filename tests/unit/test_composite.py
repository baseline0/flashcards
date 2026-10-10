"""Composite decks pin subdecks, mask slides by tag, and refuse a stale or mismatched pin.

Happy path: a tag query masks exactly the matching slides; the presentation keeps subdeck and
slide order; a composite round-trips through YAML.
Unhappy paths: a changed subdeck version, a missing subdeck, a short mask, duplicate slide
titles, and an unknown include tag all fail loudly.
"""

import json
from pathlib import Path

import pytest

from flashcards.composite import (
    AtomicDeck,
    CompositeDeck,
    PinError,
    SubdeckPin,
    build_composite,
    deck_version,
    load_atomic_deck,
    present,
    read_composite,
    slide_id,
    write_composite,
)
from flashcards.taxonomy import UnknownTagError, load_taxonomy


@pytest.fixture
def taxonomy(tmp_path: Path):
    path = tmp_path / "taxonomy.yaml"
    path.write_text("tags:\n  alpha:\n    synonyms: [Alpha Tag]\n  beta:\n    description: x\n")
    return load_taxonomy(path)


def write_glossary(path: Path, cards: list[tuple[str, str, list[str]]]) -> Path:
    data = [{"title": t, "body": b, "metadata": {"tags": tags}} for t, b, tags in cards]
    path.write_text(json.dumps(data))
    return path


@pytest.fixture
def decks(tmp_path: Path, taxonomy):
    first = write_glossary(
        tmp_path / "first.json",
        [("One", "1", ["Alpha Tag"]), ("Two", "2", ["beta"]), ("Three", "3", ["alpha"])],
    )
    second = write_glossary(
        tmp_path / "second.json", [("Four", "4", ["beta"]), ("Five", "5", ["alpha"])]
    )
    return {
        "first": load_atomic_deck("first", first, taxonomy),
        "second": load_atomic_deck("second", second, taxonomy),
    }


def test_slide_id_is_stable_and_scoped_to_its_deck():
    assert slide_id("first", "One") == slide_id("first", "One")
    assert slide_id("first", "One") != slide_id("second", "One")


def test_deck_version_changes_only_with_content(decks, taxonomy, tmp_path):
    same = load_atomic_deck("first", tmp_path / "first.json", taxonomy)
    assert same.version == decks["first"].version

    edited = AtomicDeck("first", deck_version(decks["first"].slides[:1]), decks["first"].slides[:1])
    assert edited.version != decks["first"].version


def test_duplicate_titles_fail_to_load(tmp_path: Path, taxonomy):
    path = write_glossary(tmp_path / "dup.json", [("Same", "a", []), ("Same", "b", [])])

    with pytest.raises(ValueError, match="titles must be unique"):
        load_atomic_deck("dup", path, taxonomy)


def test_tag_query_masks_exactly_the_matching_slides(decks, taxonomy):
    composite = build_composite("mix", {"Alpha Tag"}, decks, taxonomy)

    by_deck = {pin.deck: pin.mask for pin in composite.subdecks}
    assert by_deck == {"first": (1, 0, 1), "second": (0, 1)}


def test_decks_with_no_matching_slide_are_not_pinned(decks, taxonomy):
    composite = build_composite("only-beta", {"beta"}, decks, taxonomy)

    assert [pin.deck for pin in composite.subdecks] == ["first", "second"]
    only_second = build_composite("gamma", {"alpha"}, {"second": decks["second"]}, taxonomy)
    assert [pin.deck for pin in only_second.subdecks] == ["second"]


def test_presentation_keeps_subdeck_then_slide_order(decks, taxonomy):
    composite = build_composite("mix", {"alpha"}, decks, taxonomy)

    titles = [slide.title for slide in present(composite, decks)]
    assert titles == ["One", "Three", "Five"]


def test_changed_subdeck_version_is_refused(decks, taxonomy):
    composite = build_composite("mix", {"alpha"}, decks, taxonomy)
    changed = dict(decks)
    changed["first"] = AtomicDeck("first", "v-new", decks["first"].slides)

    with pytest.raises(PinError, match="rebuild the composite"):
        present(composite, changed)


def test_missing_subdeck_is_refused(decks, taxonomy):
    composite = build_composite("mix", {"alpha"}, decks, taxonomy)

    with pytest.raises(PinError, match="missing"):
        present(composite, {"first": decks["first"]})


def test_mask_shorter_than_its_subdeck_is_refused(decks, taxonomy):
    composite = build_composite("mix", {"alpha"}, decks, taxonomy)
    short = CompositeDeck(
        name="mix",
        include_tags=composite.include_tags,
        subdecks=(SubdeckPin(deck="first", version=decks["first"].version, mask=(1,)),),
    )

    with pytest.raises(PinError, match="mask for first"):
        present(short, decks)


def test_unknown_include_tag_is_refused(decks, taxonomy):
    with pytest.raises(UnknownTagError):
        build_composite("bad", {"gamma"}, decks, taxonomy)


def test_composite_round_trips_through_yaml(decks, taxonomy, tmp_path):
    composite = build_composite("mix", {"alpha"}, decks, taxonomy)
    path = tmp_path / "mix.deck.yaml"

    write_composite(composite, path)

    assert read_composite(path) == composite
