"""A composite lists its subdecks in order, each with the tags it shows, and pins what those tags produced.

Happy path: each subdeck shows its own tags' slides, in the order the composite lists the subdecks; a built
composite round-trips through YAML.
Unhappy paths: an unbuilt composite, a changed or missing subdeck, a short mask, a repeated or empty subdeck,
an unknown tag, and a legacy top-level include_tags all fail loudly.
"""

import json
from pathlib import Path

import pytest

from flashcards.composite import (
    AtomicDeck,
    CompositeDeck,
    PinError,
    SubdeckPin,
    deck_version,
    load_atomic_deck,
    pin_composite,
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
    second = write_glossary(tmp_path / "second.json", [("Four", "4", ["beta"]), ("Five", "5", ["alpha"])])
    return {
        "first": load_atomic_deck("first", first, taxonomy),
        "second": load_atomic_deck("second", second, taxonomy),
    }


def definition(name: str, *subdecks: tuple[str, set[str]]) -> CompositeDeck:
    """An authored composite: subdecks in the given order, each with its include tags."""
    return CompositeDeck(
        name=name,
        subdecks=tuple(SubdeckPin(deck=deck, include_tags=frozenset(tags)) for deck, tags in subdecks),
    )


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


def test_each_subdeck_masks_its_own_tags(decks, taxonomy):
    composite = pin_composite(
        definition("mix", ("first", {"Alpha Tag"}), ("second", {"beta"})),
        decks,
        taxonomy,
    )

    by_deck = {pin.deck: pin.mask for pin in composite.subdecks}
    assert by_deck == {"first": (1, 0, 1), "second": (1, 0)}


def test_presentation_follows_the_order_the_composite_lists_subdecks(decks, taxonomy):
    composite = pin_composite(
        definition("reversed", ("second", {"alpha"}), ("first", {"alpha"})),
        decks,
        taxonomy,
    )

    assert [slide.title for slide in present(composite, decks)] == ["Five", "One", "Three"]


def test_only_listed_subdecks_are_presented(decks, taxonomy):
    composite = pin_composite(definition("only-second", ("second", {"alpha"})), decks, taxonomy)

    assert [pin.deck for pin in composite.subdecks] == ["second"]
    assert [slide.title for slide in present(composite, decks)] == ["Five"]


def test_each_subdeck_can_show_a_different_tag(decks, taxonomy):
    composite = pin_composite(
        definition("mixed", ("first", {"beta"}), ("second", {"alpha"})),
        decks,
        taxonomy,
    )

    assert [slide.title for slide in present(composite, decks)] == ["Two", "Five"]


def test_a_subdeck_whose_tags_match_no_slide_is_refused(tmp_path: Path, taxonomy):
    beta_only = write_glossary(tmp_path / "beta_only.json", [("Only", "x", ["beta"])])
    decks = {"beta_only": load_atomic_deck("beta_only", beta_only, taxonomy)}

    with pytest.raises(ValueError, match="no slide tagged"):
        pin_composite(definition("empty", ("beta_only", {"alpha"})), decks, taxonomy)


def test_a_subdeck_listed_twice_is_refused(decks, taxonomy):
    with pytest.raises(ValueError, match="listed more than once"):
        pin_composite(definition("twice", ("first", {"alpha"}), ("first", {"beta"})), decks, taxonomy)


def test_a_subdeck_that_does_not_exist_is_refused(decks, taxonomy):
    with pytest.raises(ValueError, match="does not exist"):
        pin_composite(definition("ghost", ("nowhere", {"alpha"})), decks, taxonomy)


def test_an_unbuilt_composite_is_refused_by_presentation(decks):
    with pytest.raises(PinError, match="not built"):
        present(definition("draft", ("first", {"alpha"})), decks)


def test_changed_subdeck_version_is_refused(decks, taxonomy):
    composite = pin_composite(definition("mix", ("first", {"alpha"})), decks, taxonomy)
    changed = dict(decks)
    changed["first"] = AtomicDeck("first", "v-new", decks["first"].slides)

    with pytest.raises(PinError, match="rebuild the composite"):
        present(composite, changed)


def test_missing_subdeck_is_refused(decks, taxonomy):
    composite = pin_composite(definition("mix", ("first", {"alpha"})), decks, taxonomy)

    with pytest.raises(PinError, match="missing"):
        present(composite, {"second": decks["second"]})


def test_mask_shorter_than_its_subdeck_is_refused(decks, taxonomy):
    short = CompositeDeck(
        name="mix",
        subdecks=(
            SubdeckPin(
                deck="first",
                include_tags=frozenset({"alpha"}),
                version=decks["first"].version,
                mask=(1,),
            ),
        ),
    )

    with pytest.raises(PinError, match="mask for first"):
        present(short, decks)


def test_unknown_include_tag_is_refused(decks, taxonomy):
    with pytest.raises(UnknownTagError):
        pin_composite(definition("bad", ("first", {"gamma"})), decks, taxonomy)


def test_built_composite_round_trips_through_yaml(decks, taxonomy, tmp_path):
    composite = pin_composite(definition("mix", ("second", {"alpha"}), ("first", {"beta"})), decks, taxonomy)
    path = tmp_path / "mix.deck.yaml"

    write_composite(composite, path)

    assert read_composite(path) == composite


def test_legacy_top_level_include_tags_is_refused(tmp_path: Path):
    path = tmp_path / "old.deck.yaml"
    path.write_text("name: old\ninclude_tags: [alpha]\nsubdecks: []\n")

    with pytest.raises(ValueError, match="move it under subdecks"):
        read_composite(path)


def test_composite_sharing_an_atomic_basename_is_refused():
    from flashcards.composite import check_name_collisions

    with pytest.raises(ValueError, match=r"collide.*llm_and_recommendation_systems"):
        check_name_collisions({"machine_learning/llm_and_recommendation_systems"}, {"llm_and_recommendation_systems"})


def test_distinct_names_pass_the_collision_check():
    from flashcards.composite import check_name_collisions

    check_name_collisions({"machine_learning/bert"}, {"llm_and_recommendation_track"})


def test_composite_file_must_be_named_after_its_composite(decks, taxonomy, tmp_path):
    from flashcards.composite import load_composites

    composite = pin_composite(definition("mix", ("first", {"alpha"})), decks, taxonomy)
    write_composite(composite, tmp_path / "wrong.deck.yaml")

    with pytest.raises(ValueError, match=r"must be named mix.deck.yaml"):
        load_composites(tmp_path)


def test_card_count_is_the_number_of_masked_slides(decks, taxonomy):
    from flashcards.composite import composite_card_count

    composite = pin_composite(definition("mix", ("first", {"alpha"}), ("second", {"alpha"})), decks, taxonomy)

    assert composite_card_count(composite) == len(present(composite, decks))
