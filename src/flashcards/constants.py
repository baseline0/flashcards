"""Repository root for the flashcards package."""

from pathlib import Path

# This repository's root: src/flashcards/constants.py -> repo root
REPO_ROOT: Path = Path(__file__).resolve().parents[2]
