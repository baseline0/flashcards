from datetime import datetime, timedelta

from fsrs import Rating, FSRS, Card, RevLogEntry


class FSRSEngine:
    """Wrapper around py-fsrs for spaced repetition scheduling."""

    def __init__(self):
        self.fsrs = FSRS()

    def schedule(self, card: Card, rating: Rating) -> tuple[Card, timedelta]:
        """Apply review rating and return updated card and due offset."""
        scheduled_cards = self.fsrs.repeat(card, rating)
        return scheduled_cards[rating], timedelta(days=1)

    def card_from_flashcard(self, flashcard) -> Card:
        """Convert flashcard model to py-fsrs Card."""
        return Card(
            due=flashcard.due_date,
            stability=flashcard.stability,
            difficulty=flashcard.difficulty,
            elapsed_days=0,
            scheduled_days=0,
            reps=flashcard.repetition_count,
            lapses=0,
            state=0,  # New
            last_review=None,
        )

    def flashcard_from_card(self, card: Card, flashcard) -> None:
        """Update flashcard with new card state."""
        flashcard.stability = card.stability
        flashcard.difficulty = card.difficulty
        flashcard.repetition_count = card.reps
        flashcard.due_date = card.due
