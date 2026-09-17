# Repository Boundaries: flashcards

**Type**: Service (Learning Platform)
**Language**: Python
**Ownership**: Mark

Flashcards is a spaced-repetition learning application. Owns user account management, deck creation/editing, card lifecycle, review scheduling, and learning analytics. Provides REST APIs for learning, supports mobile/web clients, manages learning state and progress tracking.

### Provides
- REST API for cards, decks, reviews
- Database schema for user accounts and learning state
- CLI commands for fleet-ops coordination

### Depends On
- fleet-base (CLI foundation, logging)
- fleet-ops (orchestration, governance)

See `BOUNDARIES.md` in repo root for detailed charter.
