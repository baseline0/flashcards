# Flashcards Project Configuration

## Quick Start

```bash
# Install dependencies with uv
uv sync

# Run tests
pytest tests/

# Run FastAPI server
uvicorn src.flashcards.server.app:app --reload
```

## Project Structure

- **src/flashcards/** — Main application code
  - `core/` — Config, database setup (SQLAlchemy + SQLite)
  - `domains/` — Pydantic schemas, SQLAlchemy ORM models
  - `ingestion/` — Glossary parsers (JSON, Markdown, CSV, YAML)
  - `generators/` — Card synthesis engines (strategy pattern)
  - `srs/` — FSRS spaced repetition scheduler
  - `exporters/` — Output formats (Anki .apkg, JSON)
  - `server/` — FastAPI routes and web UI
- **data/raw_glossaries/** — Source glossary files by domain
- **tests/** — Pytest suite

## Architecture Principles

1. **Domain-agnostic**: Any glossary (insurance, philosophy, physics) fits the same pipeline.
2. **Strategy pattern**: Each card generator defines how a glossary entry becomes cards.
3. **Pydantic v2 validation**: All I/O validated via schemas; ORM models separate.
4. **Local-first SRS**: FSRS engine runs locally; no external API.
5. **Flat file or SQLite**: No Alembic migrations; models auto-create on startup.

## Adding New Glossary Domains

1. Create JSON file in `data/raw_glossaries/{domain}/` with entries: `[{"title": "...", "body": "...", "metadata": {...}}]`
2. Implement domain-specific card generator (extend `BaseCardGenerator`)
3. Add parser for glossary format (extend `BaseGlossaryParser`)
4. Plumb into FastAPI routes

## Testing

- Unit tests only (no integration tests yet)
- Fixtures in `conftest.py` (if needed)
- Run: `pytest tests/ -v`

## Future Work

- [ ] Scraper for authoritative glossaries (NAIC, academic databases)
- [ ] Anki exporter (genanki integration)
- [ ] HTMX UI for study sessions
- [ ] FSRS integration in review endpoint
- [ ] Multiple glossary formats (Markdown, CSV, YAML)
