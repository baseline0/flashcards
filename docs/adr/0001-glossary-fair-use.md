# ADR 0001: Fair Use and Compliance for Scraped Glossaries

**Status:** Accepted
**Date:** 2026-09-16
**Deciders:** Mark Alexiuk

## Context

Flashcards ingests glossary data from authoritative sources (academic databases, industry standards, open-access repositories). We need a principled approach to sourcing, attribution, license compliance, and provenance for every glossary term. Examples, metadata schemas, and the action items are in `docs/adr-notes/0001-glossary-fair-use.md`.

## Decision

We adopt a **three-tier sourcing model**. Every source is classified before scraping, and every glossary term records its tier and provenance metadata.

- **Tier 1 (open-access):** sources designed for reuse, such as public-domain government and standards glossaries, CC-BY and permissive-license repositories. Record the license and attribution text.
- **Tier 2 (fair use):** sources that are not open-access but qualify as transformative educational use under 17 U.S.C. § 107. Each source needs a written `fair_use_justification`, an educational disclaimer, and `commercial_use: false` unless permission is obtained.
- **Tier 3 (prohibited):** paywalled content, sources whose terms forbid scraping, licensed material restricted to non-commercial or academic use, and any source without clear ownership or license. Never scraped.

Governance:

- Tier 2 glossaries cannot appear in paid products without re-licensing (`commercial_use: false`).
- Scrapers identify themselves and are rate-limited and run off-peak (values in the notes).
- Any new glossary addition needs a tier classification, populated metadata, a fair use justification for Tier 2, and maintainer PR review before merge.
- Takedown requests remove the glossary immediately and notify users; the fair use defense is reviewed with counsel before any republish.
- Sources are audited quarterly for license changes or removal requests.

## Consequences

- Every glossary has documented provenance and compliance reasoning, and original authors are credited.
- Open-access and fair-use adaptations are both supported.
- Tier 2 depends on a template justification plus quarterly audit; specific sources escalate to legal if challenged.
- Coverage is narrower than a fair-use-everywhere policy, because Tier 3 is excluded outright.

Guard: none yet. The `GlossaryAudit` class in `src/flashcards/tools/glossary_audit.py` reports missing tiers and commercial-use gaps, but it runs only as a manual CLI (`--check-tiers`, `--check-attribution`). No test or hook enforces it.

Review-by: at the next quarterly source audit, and before any commercial release of the platform.

---

## Approval

**Deciders:** Mark Alexiuk
