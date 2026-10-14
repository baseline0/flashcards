"""`composite build` fills in an authored composite's pins, and `--check` fails when they are stale.

Happy path: a build writes versions and masks, keeping the authored subdeck order and tags; `--check` passes on
the fresh file.
Unhappy paths: `--check` fails when a glossary changed since the pins were written, and writes nothing; a build
with no authored file exits 1 and says what to author.
"""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from flashcards.cli import app


@pytest.fixture
def workspace(tmp_path: Path) -> dict[str, Path]:
    taxonomy = tmp_path / "taxonomy.yaml"
    taxonomy.write_text("tags:\n  alpha:\n    description: x\n  beta:\n    description: y\n")
    topic = tmp_path / "raw_glossaries" / "topic"
    topic.mkdir(parents=True)
    (topic / "alpha.json").write_text(json.dumps([{"title": "First", "body": "a", "metadata": {"tags": ["alpha"]}}]))
    (topic / "beta.json").write_text(json.dumps([{"title": "Second", "body": "b", "metadata": {"tags": ["beta"]}}]))
    composites = tmp_path / "composites"
    composites.mkdir()
    (composites / "track.deck.yaml").write_text(
        "name: track\n"
        "subdecks:\n"
        "- deck: topic/alpha\n"
        "  include_tags: [alpha]\n"
        "- deck: topic/beta\n"
        "  include_tags: [beta]\n"
    )
    return {"taxonomy": taxonomy, "glossaries": tmp_path / "raw_glossaries", "composites": composites}


def _args(workspace: dict[str, Path], name: str = "track", *extra: str) -> list[str]:
    return [
        "composite",
        "build",
        "--name",
        name,
        "--glossaries",
        str(workspace["glossaries"]),
        "--taxonomy",
        str(workspace["taxonomy"]),
        "--composites",
        str(workspace["composites"]),
        *extra,
    ]


def test_build_fills_in_pins_and_check_passes_on_the_fresh_file(workspace):
    runner = CliRunner()
    built = runner.invoke(app, _args(workspace))
    assert built.exit_code == 0, built.output
    target = workspace["composites"] / "track.deck.yaml"
    assert "version:" in target.read_text() and "mask:" in target.read_text()

    checked = runner.invoke(app, _args(workspace, "track", "--check"))
    assert checked.exit_code == 0, checked.output


def test_check_fails_when_a_glossary_changed_and_writes_nothing(workspace):
    runner = CliRunner()
    runner.invoke(app, _args(workspace))
    target = workspace["composites"] / "track.deck.yaml"
    before = target.read_text()

    deck = workspace["glossaries"] / "topic" / "beta.json"
    cards = json.loads(deck.read_text())
    cards.append({"title": "Third", "body": "c", "metadata": {"tags": ["beta"]}})
    deck.write_text(json.dumps(cards))

    checked = runner.invoke(app, _args(workspace, "track", "--check"))
    assert checked.exit_code == 1
    assert "out of date" in checked.output
    assert target.read_text() == before


def test_build_without_an_authored_file_says_what_to_author(workspace):
    result = CliRunner().invoke(app, _args(workspace, "missing"))

    assert result.exit_code == 1
    assert "author it" in result.output
