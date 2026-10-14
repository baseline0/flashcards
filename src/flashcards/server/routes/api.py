import json
import random
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from flashcards import composite
from flashcards.composite import PinError, check_name_collisions, composite_card_count, load_composites
from flashcards.core.config import settings
from flashcards.core.database import get_session
from flashcards.domains.models import FlashcardModel
from flashcards.domains.schemas import DeckInfo, Flashcard, GlossaryEntry, ReviewInput
from flashcards.generators.term_def_generator import TermDefinitionGenerator
from flashcards.ingestion.json_parser import JSONGlossaryParser
from flashcards.taxonomy import UnknownTagError, load_taxonomy

router = APIRouter()


def _store_entries(entries: list[GlossaryEntry], db: Session) -> None:
    """Generate the bidirectional cards for each entry and store them."""
    generator = TermDefinitionGenerator()
    for entry in entries:
        for card in generator.generate(entry):
            db.add(
                FlashcardModel(
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
            )
    db.commit()


def _load_atomic(domain: str, category: str, glossary_name: str, db: Session) -> None:
    """Load an atomic glossary file and generate its cards if the domain has none yet."""
    glossary_path = settings.glossaries_path / domain / f"{glossary_name}.json"

    if db.query(FlashcardModel).filter_by(domain=domain).first():
        return

    taxonomy = load_taxonomy(settings.glossaries_path.parent / "taxonomy.yaml")
    try:
        entries = JSONGlossaryParser(taxonomy).parse(glossary_path.read_text(), domain, category)
    except UnknownTagError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    _store_entries(entries, db)


def _load_composite(name: str, db: Session) -> None:
    """Load a composite deck's presented slides, under the composite's name, if it has no cards yet."""
    if db.query(FlashcardModel).filter_by(domain=name).first():
        return

    pin_file = settings.composite_decks_path / f"{name}.deck.yaml"
    if not pin_file.exists():
        raise HTTPException(status_code=404, detail=f"no composite deck named {name!r}")
    taxonomy = load_taxonomy(settings.glossaries_path.parent / "taxonomy.yaml")
    try:
        pinned = composite.read_composite(pin_file)
        decks = composite.load_all_decks(settings.glossaries_path, taxonomy)
        slides = composite.present(pinned, decks)
    except (PinError, UnknownTagError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    _store_entries(composite.composite_entries(name, slides), db)


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
            card_count = db.query(FlashcardModel).filter_by(domain=domain_path.name).count()

            if card_count == 0:
                # Count from file
                with open(glossary_file) as f:
                    data = json.load(f)
                    # bidirectional cards for list-shaped glossaries
                    card_count = len(data) * 2 if isinstance(data, list) else 2

            decks.append(
                DeckInfo(
                    domain=domain_path.name,
                    category=category,
                    glossary_name=glossary_name,
                    card_count=card_count,
                )
            )
    # Composite decks live in their own folder and may not share a name with an atomic deck.
    composites = load_composites(settings.composite_decks_path)
    atomic_names = {f"{d.parent.name}/{d.stem}" for d in settings.glossaries_path.rglob("*.json")}
    check_name_collisions(atomic_names, set(composites))
    for pinned in composites.values():
        decks.append(
            DeckInfo(
                domain=pinned.name,
                category="composite",
                glossary_name=pinned.name,
                card_count=composite_card_count(pinned),
                kind="composite",
            )
        )
    return decks


@router.post("/deck/load")
def load_deck(
    domain: str,
    category: str,
    glossary_name: str,
    kind: Literal["atomic", "composite"] = "atomic",
    db: Session = Depends(get_session),
) -> dict:
    """Load a deck's cards. A composite is keyed by its own name; its `domain` is that name too."""
    if kind == "composite":
        _load_composite(glossary_name, db)
        key = glossary_name
    else:
        _load_atomic(domain, category, glossary_name, db)
        key = domain
    card_count = db.query(FlashcardModel).filter_by(domain=key).count()
    return {"status": "loaded", "card_count": card_count}


@router.get("/deck/study", response_model=list[Flashcard])
def get_study_deck(domain: str, shuffle: bool = True, db: Session = Depends(get_session)) -> list[Flashcard]:
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
