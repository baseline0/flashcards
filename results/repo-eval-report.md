# Repo Inspection Report: flashcards

- Evaluated at: 2026-09-17T20:51:11.305437+00:00
- Mode: `static-only`
- Branch: `main`
- Commit: `93c69f73fe1c5e91d6da11973e62f9f72d229e39`
- Dirty worktree: True

## Policy
- No `.repo-config.yaml` found — no policy defined yet

## Stack
- Primary language (guess): python
- Manifests found: pyproject.toml
- Total lines of code (tracked files): 8927

## CI
- Platform: github_actions
- Config files: .github/workflows/deploy-pages.yml, .github/workflows/test.yml

## Structure
- Tracked files: 69
- Top-level dirs: .claude, .github, data, docs, src, tests

## Documentation
- README present: True
- CONTRIBUTING present: False
- Architecture docs: none

## Command Candidates

| Purpose | Name | Source | Command |
|---|---|---|---|
| unknown | test.step2 | ci_config:.github/workflows/test.yml | `uv python install ${{ matrix.python-version }}` |
| unknown | test.step3 | ci_config:.github/workflows/test.yml | `uv sync` |
| test | test.step4 | ci_config:.github/workflows/test.yml | `uv run pytest tests/ -v` |
| unknown | default | justfile:justfile:7 | `@just --list` |
| unknown | server | justfile:justfile:11 | `uv run uvicorn flashcards.server.app:app --reload --host 127.0.0.1 --port 8000` |
| unknown | insurance | justfile:justfile:24 | `@echo "📚 Insurance Flashcards"` |
| unknown | insurance | justfile:justfile:25 | `@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"` |
| unknown | insurance | justfile:justfile:26 | `@python3 -c "import json; data = json.load(open('data/raw_glossaries/insurance/property_and_casualty.json')); print(f'\n✅ Property & Casualty ({len(data)} terms):'); [print(f'  • {item[\"title\"]}') for item in data[:5]]; print(f'  ... and {len(data)-5} more' if len(data) > 5 else '')"` ⚠️ chained |
| unknown | insurance | justfile:justfile:27 | `@python3 -c "import json; data = json.load(open('data/raw_glossaries/insurance/underwriting_and_claims.json')); print(f'\n✅ Underwriting & Claims ({len(data)} terms):'); [print(f'  • {item[\"title\"]}') for item in data[:5]]; print(f'  ... and {len(data)-5} more' if len(data) > 5 else '')"` ⚠️ chained |
| unknown | insurance | justfile:justfile:28 | `@echo ""` |
| unknown | insurance | justfile:justfile:29 | `@echo "📖 To start the server: just server"` |
| test | insurance | justfile:justfile:30 | `@echo "🧪 To run tests: just test"` |
| unknown | insurance | justfile:justfile:31 | `@echo ""` |
| test | test | justfile:justfile:35 | `uv run pytest tests/ -v` |
| test | coverage | justfile:justfile:39 | `uv run pytest tests/ --cov=src/flashcards --cov-report=html` |
| lint | fmt | justfile:justfile:43 | `uv run ruff format .` |
| lint | fmt | justfile:justfile:44 | `uv run ruff check --fix .` |
| unknown | check | justfile:justfile:48 | `uv run pyright src/` |
| unknown | install | justfile:justfile:52 | `uv sync --dev` |
| test | clean | justfile:justfile:56 | `rm -rf .pytest_cache .ruff_cache __pycache__ .pytype` |
| unknown | clean | justfile:justfile:57 | `find . -type d -name "__pycache__" -exec rm -rf {} +` |
| test | pytest (from pyproject.toml config) | package_scripts:pyproject.toml | `pytest` |
| lint | ruff (config found in pyproject.toml) | package_scripts:pyproject.toml | `ruff check .` |

## Environment

| Tool | Available | Version |
|---|---|---|
| git | True | git version 2.35.1 |
| python | True | Python 3.13.15 |
| uv | True | uv 0.12.13 (x86_64-unknown-linux-gnu) |
| ruff | True | ruff 0.16.8 |
| mypy | False | - |
| just | True | just 1.58.0 |
| gh | True | gh version 2.74.0-19-gea8fc856e (2025-06-09) |
| node | True | v24.13.0 |
| npm | True | 11.6.2 |
| cargo | False | - |
| go | False | - |

## Unknowns

- **policy**: No .repo-config.yaml found. What risk level, quality gates, and lenses should apply to this repo?
  - Evidence: Checked for .repo-config.yaml at repo root; not found
- **command_conflict**: Multiple distinct 'test' commands were found across sources. Which is authoritative?
  - Evidence: ci_config:.github/workflows/test.yml -> uv run pytest tests/ -v; justfile:justfile -> @echo "🧪 To run tests: just test"; justfile:justfile -> uv run pytest tests/ -v; justfile:justfile -> uv run pytest tests/ --cov=src/flashcards --cov-report=html; justfile:justfile -> rm -rf .pytest_cache .ruff_cache __pycache__ .pytype; package_scripts:pyproject.toml -> pytest
- **command_conflict**: Multiple distinct 'lint' commands were found across sources. Which is authoritative?
  - Evidence: justfile:justfile -> uv run ruff format .; justfile:justfile -> uv run ruff check --fix .; package_scripts:pyproject.toml -> ruff check .
- **chained_command**: Command 'insurance' chains multiple steps with && or ;. Should these be split into independent, separately-captured commands?
  - Evidence: justfile:justfile:26 -> @python3 -c "import json; data = json.load(open('data/raw_glossaries/insurance/property_and_casualty.json')); print(f'\n✅ Property & Casualty ({len(data)} terms):'); [print(f'  • {item[\"title\"]}') for item in data[:5]]; print(f'  ... and {len(data)-5} more' if len(data) > 5 else '')"
- **chained_command**: Command 'insurance' chains multiple steps with && or ;. Should these be split into independent, separately-captured commands?
  - Evidence: justfile:justfile:27 -> @python3 -c "import json; data = json.load(open('data/raw_glossaries/insurance/underwriting_and_claims.json')); print(f'\n✅ Underwriting & Claims ({len(data)} terms):'); [print(f'  • {item[\"title\"]}') for item in data[:5]]; print(f'  ... and {len(data)-5} more' if len(data) > 5 else '')"

## Assumptions

- **stack**: Primary language is python (confidence: 0.8) — Inferred from highest line count by file extension among tracked files

## Safety
- Git status before: dirty
- Git status after: dirty
- Unexpected changes detected: False
