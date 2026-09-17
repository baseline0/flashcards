# Repository Boundaries: flashcards

**Use this file as your executable charter.** When code or dependencies drift from this contract, it signals architecture debt.

---

## Domain & Bounded Context

**What this repo owns:**

Flashcards is a spaced-repetition learning application. Owns user account management, deck creation/editing, card lifecycle, review scheduling, and learning analytics. Provides REST APIs for learning, supports mobile/web clients, manages learning state and progress tracking.

---

## Explicitly NOT (Anti-Goals)

This repo **does not** handle:

- [ ] **Authentication infrastructure** — Delegates to fleet-ops (future auth layer)
- [ ] **Fleet orchestration** — That's fleet-ops's responsibility
- [ ] **Other domain applications** — Each app is independent

---

## Upstream & Downstream Topology

### Provides (This repo exports)

| **Component** | **Type** | **Consumers** | **Contract** |
|---|---|---|---|
| REST API | HTTP | Mobile/web clients | JSON endpoints for cards, decks, reviews |
| Database Schema | PostgreSQL | Internal only | User accounts, decks, cards, reviews |
| CLI Commands | FleetCommand | fleet-ops | health, migrate, backup commands |

### Depends On (Upstream)

| **Dependency** | **Version** | **Why** | **Used By** |
|---|---|---|---|
| `fleet-base` | ^0.1.0 | CLI foundation, logging | CLI commands |
| `fleet-ops` | ^1.0 (future) | Orchestration, governance | Monitoring, deployment |

---

## Code Ownership & Governance

**Domain Owners:**
- @malexiuk

**Approval Required For:**
- ✅ Changing REST API contracts
- ✅ Database schema migrations
- ✅ Adding external service dependencies

---

## Recent Changes

| **Date** | **Change** | **ADR** | **Justification** |
|---|---|---|---|
| 2026-09-17 | Established flashcards as application domain | [ADR-400](./docs/adr/400-learning-domain.md) | Enable fleet governance of learning platform |
