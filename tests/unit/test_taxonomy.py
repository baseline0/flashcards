"""The canonical taxonomy resolves every glossary tag and rejects ambiguous or unknown ones.

Happy path: the shipped taxonomy loads, every raw tag in every glossary resolves, and
resolution ignores case.
Unhappy paths: an unknown tag raises; a spelling claimed by two canonical tags fails to load;
a non-kebab canonical name fails to load.
"""

import json

import pytest

from flashcards.constants import REPO_ROOT
from flashcards.taxonomy import UnknownTagError, load_taxonomy

TAXONOMY_FILE = REPO_ROOT / "data" / "taxonomy.yaml"
GLOSSARIES = REPO_ROOT / "data" / "raw_glossaries"


@pytest.fixture(scope="module")
def taxonomy():
    return load_taxonomy(TAXONOMY_FILE)


def raw_tags() -> set[str]:
    tags: set[str] = set()
    for path in GLOSSARIES.rglob("*.json"):
        for entry in json.loads(path.read_text()):
            tags.update(entry.get("metadata", {}).get("tags", []))
    return tags


def test_shipped_taxonomy_loads(taxonomy):
    assert "llm" in taxonomy.canonical
    assert "bert" in taxonomy.canonical


def test_every_glossary_tag_resolves_to_a_canonical_tag(taxonomy):
    unresolved = sorted(t for t in raw_tags() if taxonomy.resolve(t) not in taxonomy.canonical)
    assert unresolved == []


def test_resolution_ignores_case_and_surrounding_space(taxonomy):
    assert taxonomy.resolve("LLM") == "llm"
    assert taxonomy.resolve("  ML Infrastructure ") == "infrastructure"


def test_synonyms_map_to_their_canonical_tag(taxonomy):
    assert taxonomy.resolve("Self-Attention") == "attention"
    assert taxonomy.resolve("Bert Deck") == "bert"


def test_unknown_tag_raises(taxonomy):
    with pytest.raises(UnknownTagError, match="unknown tag 'Quantum'"):
        taxonomy.resolve("Quantum")


def test_spelling_claimed_twice_fails_to_load(tmp_path):
    path = tmp_path / "taxonomy.yaml"
    path.write_text("tags:\n  alpha:\n    synonyms: [Shared]\n  beta:\n    synonyms: [shared]\n")

    with pytest.raises(ValueError, match="claimed by both"):
        load_taxonomy(path)


def test_non_kebab_canonical_name_fails_to_load(tmp_path):
    path = tmp_path / "taxonomy.yaml"
    path.write_text("tags:\n  Machine Learning:\n    description: x\n")

    with pytest.raises(ValueError, match="lowercase kebab-case"):
        load_taxonomy(path)
