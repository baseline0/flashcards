# flashcards

<!-- fleet-standard:begin -->
**Universal rules:** `~/.claude/CLAUDE.md` (fleet standard 1.4.0).
<!-- fleet-standard:end -->

Commands are in the justfile (`just --list`). Universal rules are in `~/.claude/CLAUDE.md`.

## Rules that are not visible in the code

- Composite decks are authored (`data/composite_decks/*.deck.yaml`: subdecks, order, include_tags). `just composite-build` fills in pins; `just composite-check` fails when they are stale. Never hand-edit `version` or `mask`.
- Coverage floors in `pyproject.toml` are a ratchet: raise them, never lower them.
- The pyright baseline (`pyright-baseline.json`) is a ratchet: `fleet ratchet update` only after errors are removed.
- `TODO.md` is a local backlog, gitignored. Completed items are deleted, not checked off.
- The database gets new nullable columns on startup (`add_missing_columns`). Anything else needs a deliberate migration.
