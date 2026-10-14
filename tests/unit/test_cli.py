"""The composite-build command regenerates pins and fails `--check` when the committed file is stale.

Happy path: a build writes the pin file, and `--check` passes on the fresh file.
Unhappy path: `--check` fails when a glossary changed since the pin was written, and writes nothing.
"""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from flashcards.cli import app


@pytest.fixture
def workspace(tmp_path: Path) -> dict[str, Path]:
    taxonomy = tmp_path / "taxonomy.yaml"
    taxonomy.write_text("tags:\n  alpha:\n    description: x\n")
    glossaries = tmp_path / "raw_glossaries" / "topic"
    glossaries.mkdir(parents=True)
    (glossaries / "deck.json").write_text(
        json.dumps(
            [
                {"title": "First", "body": "a", "metadata": {"tags": ["alpha"]}},
                {"title": "Second", "body": "b", "metadata": {"tags": []}},
            ]
        )
    )
    composites = tmp_path / "composites"
    composites.mkdir()
    return {"taxonomy": taxonomy, "glossaries": tmp_path / "raw_glossaries", "composites": composites}


def _args(workspace: dict[str, Path], *extra: str) -> list[str]:
    return [
        "composite",
        "build",
        "--name",
        "alpha_track",
        "--include-tag",
        "alpha",
        "--glossaries",
        str(workspace["glossaries"]),
        "--taxonomy",
        str(workspace["taxonomy"]),
        "--composites",
        str(workspace["composites"]),
        *extra,
    ]


def test_build_writes_pins_and_check_passes_on_the_fresh_file(workspace):
    runner = CliRunner()
    built = runner.invoke(app, _args(workspace))
    assert built.exit_code == 0, built.output
    target = workspace["composites"] / "alpha_track.deck.yaml"
    assert target.exists()

    checked = runner.invoke(app, _args(workspace, "--check"))
    assert checked.exit_code == 0, checked.output


def test_check_fails_when_a_glossary_changed_and_writes_nothing(workspace):
    runner = CliRunner()
    runner.invoke(app, _args(workspace))
    target = workspace["composites"] / "alpha_track.deck.yaml"
    before = target.read_text()

    deck = workspace["glossaries"] / "topic" / "deck.json"
    cards = json.loads(deck.read_text())
    cards.append({"title": "Third", "body": "c", "metadata": {"tags": ["alpha"]}})
    deck.write_text(json.dumps(cards))

    checked = runner.invoke(app, _args(workspace, "--check"))
    assert checked.exit_code == 1
    assert "out of date" in checked.output
    assert target.read_text() == before
