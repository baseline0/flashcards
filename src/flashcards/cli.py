"""Command-line entry point for flashcards.

`composite build` regenerates a composite deck's pin file from the glossaries, so a composite is never
hand-edited. Its `--check` mode exits non-zero when the committed file is out of date, for CI and `just`.
"""

from pathlib import Path

import click
import typer

from flashcards import composite
from flashcards.taxonomy import load_taxonomy

app = typer.Typer(help="Flashcards: glossaries, composite decks, and the study server.", add_completion=False)
composite_app = typer.Typer(help="Composite decks: subdeck pins and slide masks.", add_completion=False)
app.add_typer(composite_app, name="composite")


@composite_app.command("build")
def composite_build(
    name: str = typer.Option(..., "--name", help="Composite deck name; its file is <name>.deck.yaml"),
    glossaries: Path = typer.Option(..., "--glossaries", help="Glossary root, e.g. data/raw_glossaries"),
    taxonomy: Path = typer.Option(..., "--taxonomy", help="Taxonomy file, e.g. data/taxonomy.yaml"),
    composites: Path = typer.Option(..., "--composites", help="Composite deck folder, e.g. data/composite_decks"),
    check: str = typer.Option(
        ...,
        "--check",
        click_type=click.Choice(["true", "false"]),
        help="true: write nothing and exit 1 if the file would change; false: write the file",
    ),
) -> None:
    """Fill in each authored subdeck's version and mask, keeping the subdeck order and tags as written."""
    checking = check == "true"
    target = composites / f"{name}.deck.yaml"
    if not target.exists():
        typer.echo(f"{target} does not exist; author it with its subdecks and include_tags first", err=True)
        raise typer.Exit(code=1)

    tax = load_taxonomy(taxonomy)
    decks = composite.load_all_decks(glossaries, tax)
    try:
        definition = composite.read_composite(target)
        built = composite.pin_composite(definition, decks, tax)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    if checking:
        if built != definition:
            typer.echo(f"{target} is out of date; run `flashcards composite build` to regenerate it", err=True)
            raise typer.Exit(code=1)
        typer.echo(f"{target} is up to date")
        return

    composite.write_composite(built, target)
    typer.echo(f"wrote {target}: {len(built.subdecks)} subdecks")
