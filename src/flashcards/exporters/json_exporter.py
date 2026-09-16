import json
from pathlib import Path

from ..domains.schemas import Flashcard


class JSONExporter:
    """Export flashcards to JSON format."""

    def export(self, flashcards: list[Flashcard], output_path: Path) -> None:
        """Write flashcards to JSON file."""
        data = [card.model_dump() for card in flashcards]
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
