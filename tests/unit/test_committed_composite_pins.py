"""The committed composite deck pins match the glossaries they were built from.

Design intent: a composite's version and mask are generated, so a stale or hand-edited pin is caught by the test
gate, not only by a separate `just composite-check` run.
Happy path: every committed composite passes `composite build --check true` against the committed data.
"""

from typer.testing import CliRunner

from flashcards.cli import app
from flashcards.constants import REPO_ROOT as REPO


def test_every_committed_composite_pin_matches_its_glossaries():
    """Each composite's pins are up to date with the committed glossaries and taxonomy (no hand edits)."""
    composites = sorted((REPO / "data" / "composite_decks").glob("*.deck.yaml"))
    assert composites, "no committed composite decks found"
    runner = CliRunner()
    for path in composites:
        name = path.name.removesuffix(".deck.yaml")
        result = runner.invoke(
            app,
            [
                "composite",
                "build",
                "--name",
                name,
                "--glossaries",
                str(REPO / "data" / "raw_glossaries"),
                "--taxonomy",
                str(REPO / "data" / "taxonomy.yaml"),
                "--composites",
                str(REPO / "data" / "composite_decks"),
                "--check",
                "true",
            ],
        )
        assert result.exit_code == 0, f"{name} pins are stale: {result.output}"
