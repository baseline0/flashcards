# Flashcards

A modular, domain-agnostic spaced repetition system for learning from arbitrary glossaries.

## Test Status

[![Unit Tests](https://github.com/anthropics/flashcards/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/anthropics/flashcards/actions)  
**Status:** 32/32 tests passing ✅

## Features

- **Multi-domain glossaries** — Insurance, philosophy, science, history (any domain)
- **Card synthesis** — Generate term↔definition, cloze, and quote attribution cards
- **Spaced repetition** — FSRS algorithm for optimal review scheduling
- **Local storage** — SQLite database, no external dependencies
- **FastAPI server** — Glossary selection, shuffle deck, study interface
- **Export formats** — JSON, Anki .apkg (planned)

## Quick Start

```bash
# Install dependencies
uv sync

# Run tests
pytest tests/

# Start server
uvicorn src.flashcards.server.app:app --reload
```

Visit http://localhost:8000/docs for interactive API docs.

## Example: Loading Insurance Glossary

```bash
# Load P&C insurance deck
curl -X POST "http://localhost:8000/api/deck/load?domain=insurance&category=property&glossary_name=property_and_casualty"

# Get shuffled deck
curl "http://localhost:8000/api/deck/study?domain=insurance&shuffle=true"

# Record a review (rating 1-4)
curl -X POST "http://localhost:8000/api/card/review" \
  -H "Content-Type: application/json" \
  -d '{"card_id": "...", "rating": 3}'
```

## Architecture

```
[ Raw Glossaries ] → [ Parsers ] → [ Card Generators ] → [ SQLite ] → [ FastAPI ]
   (JSON, MD, etc.)                  (Strategy Pattern)               (Study UI)
                                                            ↓
                                                      [ FSRS Engine ]
```

## Data Models

### GlossaryEntry
Raw glossary entry from a file:
- `domain` (e.g., "insurance", "philosophy")
- `category` (e.g., "property", "stoicism")
- `title` (term or quote name)
- `body` (definition or text)
- `metadata` (custom fields)

### Flashcard
Generated card ready for review:
- `front` / `back` (question / answer)
- `card_type` (term_definition, cloze, quote)
- `tags` (for filtering)
- FSRS metrics: `stability`, `difficulty`, `repetition_count`, `due_date`

## Card Types

- **Term ↔ Definition** — Bidirectional recall (insurance, science)
- **Cloze Deletion** — Fill-in-the-blank (flexible for any domain)
- **Quote Attribution** — Author/source recall (philosophy, history)

## Extending

### Add a New Glossary Domain

1. Create `data/raw_glossaries/{domain}/{glossary}.json`
2. Implement `src/flashcards/generators/YourGenerator(BaseCardGenerator)`
3. Plumb into `server/routes/api.py`

### Add a New Parser

Extend `src/flashcards/ingestion/base.py`:

```python
class YAMLGlossaryParser(BaseGlossaryParser):
    def parse(self, content: str, domain: str, category: str) -> list[GlossaryEntry]:
        # Your YAML parsing logic
        pass
```

### Add a New Exporter

Extend `src/flashcards/exporters/`:

```python
class AnkiExporter:
    def export(self, flashcards: list[Flashcard], output_path: Path) -> None:
        # Generate .apkg file
        pass
```

## Technology Stack

- **Python 3.13** — Latest features, performance
- **FastAPI** — Fast, async web framework
- **SQLAlchemy 2.0** — Async ORM with SQLite
- **Pydantic v2** — Data validation
- **py-fsrs** — Modern spaced repetition scheduler
- **genanki** — Anki deck generation
- **pytest** — Unit test framework

## Project Status

**v0.1.0** — P&C insurance demo, basic FastAPI routes, FSRS framework

### TODO

- [ ] Scraper for NAIC, academic glossaries
- [ ] HTMX templates for web UI
- [ ] Full FSRS integration in review flow
- [ ] Markdown and CSV parsers
- [ ] Anki exporter integration
- [ ] User accounts and multi-deck sessions
- [ ] Quote attribution card generator

## License

MIT
