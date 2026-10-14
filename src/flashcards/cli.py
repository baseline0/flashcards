"""Command-line entry point for flashcards.

`composite build` regenerates a composite deck's pin file from the glossaries, so a composite is never
hand-edited. Its `--check` mode exits non-zero when the committed file is out of date, for CI and `just`.
"""

from pathlib import Path

import typer

from flashcards import composite
from flashcards.taxonomy import load_taxonomy

app = typer.Typer(help="Flashcards: glossaries, composite decks, and the study server.", add_completion=False)
composite_app = typer.Typer(help="Composite decks: subdeck pins and slide masks.", add_completion=False)
app.add_typer(composite_app, name="composite")


@composite_app.command("build")
def composite_build(
    name: str = typer.Option(..., "--name", help="Composite deck name; its file is <name>.deck.yaml"),
    include_tag: list[str] = typer.Option(
        ..., "--include-tag", help="Canonical or synonym tag a slide must carry (repeat for several)"
    ),
    glossaries: Path = typer.Option(Path("data/raw_glossaries"), "--glossaries", help="Glossary root"),
    taxonomy: Path = typer.Option(Path("data/taxonomy.yaml"), "--taxonomy", help="Taxonomy file"),
    composites: Path = typer.Option(Path("data/composite_decks"), "--composites", help="Composite deck folder"),
    check: bool = typer.Option(False, "--check", help="Write nothing; exit 1 if the committed file would change"),
) -> None:
    """Pin every subdeck that has a matching slide, masking exactly the matching slides."""
    tax = load_taxonomy(taxonomy)
    decks = composite.load_all_decks(glossaries, tax)
    built = composite.build_composite(name, set(include_tag), decks, tax)
    target = composites / f"{name}.deck.yaml"

    if check:
        current = composite.read_composite(target) if target.exists() else None
        if current != built:
            typer.echo(f"{target} is out of date; run `flashcards composite build` to regenerate it", err=True)
            raise typer.Exit(code=1)
        typer.echo(f"{target} is up to date")
        return

    composite.write_composite(built, target)
    typer.echo(f"wrote {target}: {len(built.subdecks)} subdeck pins")
