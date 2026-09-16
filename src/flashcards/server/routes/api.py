import json
import random
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.config import settings
from ...core.database import get_session
from ...domains.models import FlashcardModel
from ...domains.schemas import DeckInfo, Flashcard, ReviewInput
from ...generators.term_def_generator import TermDefinitionGenerator
from ...ingestion.json_parser import JSONGlossaryParser

router = APIRouter()


def _load_and_generate_deck(domain: str, category: str, glossary_name: str, db: Session):
    """Load glossary file and generate cards if not already in DB."""
    glossary_path = settings.glossaries_path / domain / f"{glossary_name}.json"

    # Check if cards already exist
    existing = db.query(FlashcardModel).filter_by(domain=domain).first()
    if existing:
        return

    # Parse and generate
    content = glossary_path.read_text()
    parser = JSONGlossaryParser()
    entries = parser.parse(content, domain, category)

    generator = TermDefinitionGenerator()
    for entry in entries:
        cards = generator.generate(entry)
        for card in cards:
            model = FlashcardModel(
                id=card.id,
                entry_id=card.entry_id,
                domain=card.domain,
                card_type=card.card_type.value,
                front=card.front,
                back=card.back,
                tags_json=json.dumps(card.tags),
                stability=card.stability,
                difficulty=card.difficulty,
                repetition_count=card.repetition_count,
                due_date=card.due_date,
            )
            db.add(model)
    db.commit()


@router.get("/decks", response_model=list[DeckInfo])
def list_decks(db: Session = Depends(get_session)) -> list[DeckInfo]:
    """List available glossary decks."""
    decks = []
    for domain_path in settings.glossaries_path.iterdir():
        if not domain_path.is_dir():
            continue

        for glossary_file in domain_path.glob("*.json"):
            glossary_name = glossary_file.stem
            category = glossary_file.parent.name

            # Count cards in DB or in file
            card_count = (
                db.query(FlashcardModel)
                .filter_by(domain=domain_path.name)
                .count()
            )

            if card_count == 0:
                # Count from file
                with open(glossary_file) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        card_count = len(data) * 2  # bidirectional
                    else:
                        card_count = 2

            decks.append(
                DeckInfo(
                    domain=domain_path.name,
                    category=category,
                    glossary_name=glossary_name,
                    card_count=card_count,
                )
            )
    return decks


@router.post("/deck/load")
def load_deck(
    domain: str, category: str, glossary_name: str, db: Session = Depends(get_session)
) -> dict:
    """Load glossary and generate cards."""
    _load_and_generate_deck(domain, category, glossary_name, db)
    card_count = db.query(FlashcardModel).filter_by(domain=domain).count()
    return {"status": "loaded", "card_count": card_count}


@router.get("/deck/study", response_model=list[Flashcard])
def get_study_deck(
    domain: str, shuffle: bool = True, db: Session = Depends(get_session)
) -> list[Flashcard]:
    """Get shuffled deck for studying."""
    cards = db.query(FlashcardModel).filter_by(domain=domain).all()

    flashcards = [
        Flashcard(
            id=card.id,
            entry_id=card.entry_id,
            domain=card.domain,
            card_type=card.card_type,
            front=card.front,
            back=card.back,
            tags=json.loads(card.tags_json),
            stability=card.stability,
            difficulty=card.difficulty,
            repetition_count=card.repetition_count,
            due_date=card.due_date,
        )
        for card in cards
    ]

    if shuffle:
        random.shuffle(flashcards)
    return flashcards


@router.post("/card/review")
def review_card(review: ReviewInput, db: Session = Depends(get_session)) -> dict:
    """Record user review of a card (placeholder for FSRS integration)."""
    card = db.query(FlashcardModel).filter_by(id=review.card_id).first()
    if not card:
        return {"error": "Card not found"}

    # TODO: Integrate FSRS engine for actual scheduling
    card.repetition_count += 1
    db.commit()

    return {"status": "reviewed", "rating": review.rating}
