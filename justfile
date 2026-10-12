#!/usr/bin/env just --justfile

# Shared commit recipe from fleet-base. Literal path: just does not interpolate variables into import paths.
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
    @uv run python -c "import json; data = json.load(open('data/raw_glossaries/insurance/property_and_casualty.json')); print(f'\n✅ Property & Casualty ({len(data)} terms):'); [print(f'  • {item[\"title\"]}') for item in data[:5]]; print(f'  ... and {len(data)-5} more' if len(data) > 5 else '')"
    @uv run python -c "import json; data = json.load(open('data/raw_glossaries/insurance/underwriting_and_claims.json')); print(f'\n✅ Underwriting & Claims ({len(data)} terms):'); [print(f'  • {item[\"title\"]}') for item in data[:5]]; print(f'  ... and {len(data)-5} more' if len(data) > 5 else '')"
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

# Pyright ratchet: fails when a file gains errors (scripts in fleet-base; mode from pyproject.toml).
check-types:
    fleet ratchet check

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

# Unit tests: the gate the pre-push hook runs (fleet hook standard, fleet_base.hook_standard R4)
test-unit:
    just test

# ============================================================================
# Shared fleet recipes, run by fleet-base's installed tool (uv tool install --editable ~/projects/fleet-base).
# Each line calls `fleet recipe NAME`; define a recipe here instead to override it.
# ============================================================================

# Falls back to manual commit if Ollama unavailable or commitmate fails
commit:
    fleet recipe commit

# Add all untracked files and commit with LLM or custom message
commit-all:
    fleet recipe commit-all
