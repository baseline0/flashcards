# ADR 0001: Fair Use and Compliance for Scraped Glossaries

**Status:** Accepted  
**Date:** 2026-09-16  
**Deciders:** Mark Alexiuk

## Context

Flashcards ingests glossary data from authoritative sources (academic databases, industry standards, open-access repositories). We need a principled approach to:

1. Determine when scraping is ethical and legally compliant
2. Attribute sources correctly
3. Maintain compliance with licenses (CC-BY, MIT, Apache, proprietary)
4. Document the provenance of every glossary term
5. Clarify our fair use justification

## Decision

We adopt a **three-tier sourcing model** with corresponding metadata requirements:

### Tier 1: Authoritative Open-Access (Preferred)
Sources explicitly designed for reuse and adaptation.

**Examples:**
- NIST Glossaries (public domain)
- CC-BY-4.0 academic papers and textbooks
- Government standards (NAIC, OSHA, EPA, etc.)
- Open textbooks (OpenStax, LibreTexts)
- GitHub repositories with permissive licenses (MIT, Apache 2.0)

**Compliance:** Copy license into `glossary.license` field. Attribute via metadata.

**Metadata required:**
```json
{
  "title": "Deductible",
  "body": "...",
  "metadata": {
    "source_url": "https://...",
    "source_name": "NAIC Glossary of Insurance Terms",
    "license": "CC-BY-4.0",
    "license_url": "https://creativecommons.org/licenses/by/4.0/",
    "attribution_required": true,
    "attribution_text": "© National Association of Insurance Commissioners (NAIC)",
    "scraped_date": "2026-09-16",
    "notes": "Glossary terms extracted from NAIC's public glossary database"
  }
}
```

### Tier 2: Fair Use Adaptation (Requires Justification)
Sources that are not explicitly open-access but qualify for fair use under U.S. Copyright law (17 U.S.C. § 107) because the work is transformative.

**Examples:**
- Academic textbooks (creating study flashcards ≠ reproducing the textbook)
- Industry whitepapers and technical documentation
- Wikipedia articles (check their license per-article)
- Published standards when reformatted as vocabulary

**Fair use justification factors:**
1. **Purpose & character:** Educational, transformative (summarized as Q&A)
2. **Nature of work:** Factual glossaries (not creative works)
3. **Amount used:** Individual definitions, not wholesale reproduction
4. **Market effect:** Flashcards enhance learning of the original text; don't substitute for it

**Compliance:**
- Include `fair_use_justification` in metadata
- Add disclaimer: "Glossary extracted for educational purposes under fair use (17 U.S.C. § 107)"
- If commercial use is planned, obtain explicit permission

**Metadata required:**
```json
{
  "metadata": {
    "source_url": "https://...",
    "source_name": "Deep Learning (Goodfellow, Bengio, Courville)",
    "license": "proprietary",
    "fair_use_justification": "Educational study aid; flashcard format is transformative",
    "commercial_use": false,
    "attribution_required": true,
    "attribution_text": "Adapted from Deep Learning (Goodfellow, Bengio, Courville, 2016)",
    "scraped_date": "2026-09-16",
    "notes": "Terms extracted from Ch. 6 (Deep Feedforward Networks) for study purposes"
  }
}
```

### Tier 3: Do Not Scrape (Prohibited)
**Avoid entirely:**
- Paywalled content (IEEE, ACM, Springer, Elsevier journals)
- Content with explicit Terms of Service forbidding scraping (e.g., LinkedIn, Stack Overflow)
- Proprietary training materials and course content
- Licensed datasets marked "non-commercial" or "academic use only"
- Any source without clear ownership or license

## Consequences

### Positive
✓ **Defensible sourcing:** Every glossary has documented provenance and compliance reasoning  
✓ **Attribution:** Original authors and organizations are credited  
✓ **Transparency:** Users understand the fair use basis  
✓ **Flexibility:** Supports both open-access and fair-use adaptations  
✓ **Maintainability:** Metadata enables auditing and re-evaluation  

### Risks Mitigated
- **Copyright claims:** Fair use documented; open-access sources have explicit permission
- **Source rot:** Record source URL and snapshot date
- **Commercial liability:** Metadata flags commercial restrictions; Tier 3 explicitly avoided

## Implementation

### Schema Updates
Update `GlossaryEntry` to track:
```python
metadata: {
    "source_url": str,           # Where the term originated
    "source_name": str,          # Human-readable source
    "license": str,              # CC-BY-4.0, MIT, Apache-2.0, proprietary, public-domain
    "license_url": str,          # Link to license text
    "attribution_required": bool,
    "attribution_text": str,     # How to attribute (author, organization, year)
    "fair_use_justification": str,  # Only for Tier 2
    "commercial_use": bool,      # Whether flashcards may be used commercially
    "scraped_date": str,         # ISO-8601 date
    "notes": str,                # Provenance notes (e.g., "Extracted from Ch. 3")
    "tier": int,                 # 1=Open-Access, 2=Fair-Use, 3=Prohibited (rejected)
}
```

### Auditing
1. Before scraping, classify source as Tier 1, 2, or 3
2. Populate metadata fields
3. When exporting (to Anki, JSON, etc.), include attribution in card back or deck notes
4. Quarterly review of sources for license changes or removal requests

### Example: Creating a Glossary
```python
# Machine Learning Glossary (Tier 1: CC-BY, NVIDIA)
[
  {
    "title": "Epoch",
    "body": "One complete pass through the training dataset",
    "metadata": {
      "source_url": "https://developer.nvidia.com/glossary/",
      "source_name": "NVIDIA AI Glossary",
      "license": "CC-BY-4.0",
      "license_url": "https://creativecommons.org/licenses/by/4.0/",
      "attribution_required": true,
      "attribution_text": "© NVIDIA",
      "tier": 1,
      "commercial_use": true,
      "scraped_date": "2026-09-16"
    }
  }
]
```

## Alternatives Considered

### A: No Metadata (Rejected)
**Risk:** Indefensible if copyright holder objects; users cannot verify sources.

### B: Tier 1 Only
**Risk:** Severely limits glossary coverage; many valuable sources require fair use argument.

### C: Aggressive Scraping (Rejected)
**Risk:** Legal liability, ethical concerns, undermines trust.

## Questions for Review

1. **Fair use threshold:** Should Tier 2 require legal review for each source, or is the justification template sufficient?
   - **Decision:** Template + quarterly audit is sufficient; escalate specific sources to legal if challenged.

2. **Commercial licensing:** If we commercialize the flashcard platform, should Tier 2 glossaries be restricted to non-commercial decks?
   - **Decision:** Yes. Metadata flag `commercial_use: false` means Tier 2 glossaries cannot be included in paid products without re-licensing.

3. **Scraper best practices:** What's the acceptable rate/volume for scraping without violating ToS?
   - **Decision:** Scrape during off-peak hours, identify as `User-Agent: flashcards-glossary-scraper/1.0`. Max 1 request per second.

4. **Takedown process:** How do we handle DMCA requests or cease-and-desist letters?
   - **Decision:** Remove glossary immediately; notify users. Evaluate fair use defense with legal counsel before republishing.

## Recommended Authoritative Sources

### Open-Access (Tier 1)
- **NIST Glossaries** (computer security, measurement, etc.) — public domain
- **NVIDIA AI Glossary** — CC-BY-4.0
- **OpenStax** (textbooks) — CC-BY-4.0
- **GitHub** (permissive licenses: MIT, Apache 2.0)
- **Wikibooks** — CC-BY-SA
- **Government agencies** (OSHA, EPA, SEC) — public domain
- **ISO/IEC Standards** (select free documents)

### Tier 2 (Fair Use with Justification)
- **Deep Learning** (Goodfellow, Bengio, Courville) — educational, transformative
- **Machine Learning Yearning** (Andrew Ng) — free for educational use
- **Kubernetes docs** (Apache 2.0) — explicit permission
- **AWS Whitepapers** — free to distribute for non-commercial purposes

### Do Not Scrape (Tier 3)
- IEEE, ACM, Springer digital libraries (paywalled)
- LinkedIn, Stack Overflow (explicit ToS forbid scraping)
- Proprietary enterprise software docs (e.g., Oracle)
- Academic papers behind paywalls (request from author instead)

## Decision Outcome

**Adopted:** Three-tier model with metadata-driven compliance.

**Action items:**
1. Update `GlossaryEntry` schema to include metadata fields
2. Create scraper templates for Tier 1 and Tier 2
3. Document sources in CSV/JSON inventory
4. Add attribution export to Anki, JSON exporters
5. Quarterly audit of all scraped glossaries

**Governance:** Any new glossary addition requires:
- Tier classification (1, 2, or 3)
- Metadata populated
- Fair use justification for Tier 2
- PR review by maintainer before merge
