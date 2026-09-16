#!/usr/bin/env just --justfile

set shell := ["bash", "-c"]

# Default: show help
default:
    @just --list

# Start local server (FastAPI + Uvicorn)
server:
    uv run uvicorn flashcards.server.app:app --reload --host 127.0.0.1 --port 8000

# Run flashcards locally (start server + open browser)
run: server
    @echo ""
    @echo "🚀 Flashcards running at:"
    @echo "📚 Study Interface: http://127.0.0.1:8000/study"
    @echo "📖 Landing Page: http://127.0.0.1:8000/"
    @echo "🔧 API Docs: http://127.0.0.1:8000/docs"
    @echo ""

# Study insurance flashcards (P&C + underwriting)
insurance:
    @echo "📚 Insurance Flashcards"
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    @python3 -c "import json; data = json.load(open('data/raw_glossaries/insurance/property_and_casualty.json')); print(f'\n✅ Property & Casualty ({len(data)} terms):'); [print(f'  • {item[\"title\"]}') for item in data[:5]]; print(f'  ... and {len(data)-5} more' if len(data) > 5 else '')"
    @python3 -c "import json; data = json.load(open('data/raw_glossaries/insurance/underwriting_and_claims.json')); print(f'\n✅ Underwriting & Claims ({len(data)} terms):'); [print(f'  • {item[\"title\"]}') for item in data[:5]]; print(f'  ... and {len(data)-5} more' if len(data) > 5 else '')"
    @echo ""
    @echo "📖 To start the server: just server"
    @echo "🧪 To run tests: just test"
    @echo ""

# Run tests
test:
    uv run pytest tests/ -v

# Run tests with coverage
coverage:
    uv run pytest tests/ --cov=src/flashcards --cov-report=html

# Format & lint
fmt:
    uv run ruff format .
    uv run ruff check --fix .

# Type check
check:
    uv run pyright src/

# Install dependencies
install:
    uv sync --dev

# Clean cache
clean:
    rm -rf .pytest_cache .ruff_cache __pycache__ .pytype
    find . -type d -name "__pycache__" -exec rm -rf {} +

# Full CI: format, check, test
ci: fmt check test
    @echo "✅ All checks passed"
