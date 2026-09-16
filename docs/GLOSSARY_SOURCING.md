# Glossary Sourcing & Compliance Guide

This document explains how to responsibly source, classify, and maintain glossaries in the Flashcards project.

## Quick Reference: Three-Tier Model

| Tier | Definition | Examples | Compliance |
|------|-----------|----------|-----------|
| **1: Open-Access** | Explicitly designed for reuse (CC-BY, MIT, public domain, Apache 2.0) | Wikipedia, OpenStax, NIST, GitHub MIT repos | Copy license; attribute via metadata |
| **2: Fair Use** | Non-open sources adapted for education; transformative use case | AWS docs, textbooks, whitepapers | Document fair use reasoning; non-commercial |
| **3: Prohibited** | Do not scrape—paywalled, explicit ToS forbid it, proprietary | IEEE, ACM, Springer, LinkedIn, Stack Overflow | Skip entirely |

**→ For a complete analysis, see [ADR 0001: Glossary Fair Use](adr/0001-glossary-fair-use.md)**

---

## Step 1: Before Scraping—Classify the Source

When you identify a glossary source, answer these questions:

### Q1: Is the source explicitly open-access?
- Check for explicit license (CC-BY, MIT, Apache 2.0, public domain)
- Look for "free to reuse," "open access," or similar language
- **Yes → Tier 1**
- **No → Go to Q2**

### Q2: Is the source behind a paywall or forbidden by ToS?
- Paywalled: IEEE, ACM, Springer, Elsevier
- ToS forbids scraping: LinkedIn, Stack Overflow
- Proprietary/restricted: Enterprise software docs
- **Yes → Tier 3 (skip it)**
- **No → Go to Q3**

### Q3: Can we justify fair use for education?
- Purpose: Creating study flashcards (transformative, non-competitive)
- Nature: Factual definitions (not creative works)
- Amount: Individual terms, not wholesale reproduction
- Market effect: Flashcards don't substitute for the original
- **Yes → Tier 2 (with documentation)**
- **No → Tier 3 (skip it)**

---

## Step 2: Populate Metadata

Every term must include complete metadata. Use this template:

### Tier 1: Open-Access Template
```json
{
  "title": "Epoch",
  "body": "One complete pass through the training dataset...",
  "metadata": {
    "source_url": "https://en.wikipedia.org/wiki/Epoch_(computing)",
    "source_name": "Wikipedia: Epoch (Computing)",
    "license": "CC-BY-SA-3.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
    "attribution_required": true,
    "attribution_text": "Wikipedia Contributors",
    "tier": 1,
    "commercial_use": true,
    "scraped_date": "2026-09-16"
  }
}
```

### Tier 2: Fair Use Template
```json
{
  "title": "EC2 Instance",
  "body": "A virtual machine on AWS...",
  "metadata": {
    "source_url": "https://docs.aws.amazon.com/ec2/",
    "source_name": "AWS EC2 Documentation",
    "license": "proprietary",
    "fair_use_justification": "Educational study aid; glossary format is transformative and non-competitive with AWS documentation",
    "attribution_required": true,
    "attribution_text": "Amazon Web Services",
    "tier": 2,
    "commercial_use": false,
    "scraped_date": "2026-09-16",
    "notes": "Definitions adapted from official AWS docs for educational purposes only"
  }
}
```

**Key differences:**
- Tier 2 includes `fair_use_justification`
- Tier 2 sets `commercial_use: false`
- Add notes explaining the adaptation

---

## Step 3: Create and Submit Glossary

### File Location
```
data/raw_glossaries/{domain}/{glossary_name}.json
```

Examples:
```
data/raw_glossaries/insurance/property_and_casualty.json
data/raw_glossaries/machine_learning/fundamentals.json
data/raw_glossaries/cloud_computing/aws_terminology.json
```

### Verify Compliance
Before committing, run the audit tool:

```bash
python -m src.flashcards.tools.glossary_audit --summary
python -m src.flashcards.tools.glossary_audit --check-tiers
python -m src.flashcards.tools.glossary_audit --check-attribution
```

Expected output:
```
✓ All 50 terms are properly classified
✓ All required attributions are present
✓ Summary by tier:
  Tier 1: 32 terms (CC-BY, Apache 2.0, public domain)
  Tier 2: 18 terms (fair use w/ justification)
  Tier 3: 0 terms (correctly skipped)
```

---

## Recommended Open-Access Sources (Tier 1)

### General
- **Wikipedia** — CC-BY-SA-3.0; broad coverage; user-contributed
- **Wikibooks** — CC-BY-SA; textbook-like depth
- **GitHub repos** — MIT, Apache 2.0, GPLv3; open source glossaries

### Technical & Science
- **NIST Glossaries** — Public domain; computer security, physics, metrology
- **NVIDIA AI Glossary** — CC-BY-4.0; GPU computing, deep learning
- **OpenStax** — CC-BY-4.0; free textbooks with glossaries
- **Kubernetes Docs** — Apache 2.0; container orchestration
- **LibreTexts** — CC-BY-SA; chemistry, biology, physics

### Government & Standards
- **OSHA** — Public domain; workplace safety and health
- **EPA** — Public domain; environmental science
- **SEC** — Public domain; finance and securities
- **NAIC** — Insurance regulatory glossaries

### Academic & Education
- **arXiv** — CC-BY, CC-BY-NC, open access preprints
- **PubMed Central** — Open access biomedical literature
- **Project MUSE** — Some open access humanities resources

---

## Tier 2 Sources (Fair Use with Caution)

These are valuable for study but require careful documentation:

### Technology & Cloud
- **AWS Whitepapers** — Free distribution for non-commercial use
- **Google Cloud documentation** — Educational use permitted
- **Azure documentation** — Similar to AWS
- **Kubernetes official docs** — Apache 2.0 (actually Tier 1)

### Textbooks
- **"Deep Learning"** (Goodfellow, Bengio, Courville) — Glossary for educational study
- **"Machine Learning Yearning"** (Andrew Ng) — Free for education
- **"Designing Data-Intensive Applications"** (Kleppmann) — Educational excerpts only

### Technical Books & Papers
- **O'Reilly books** — Educational study aids only (not wholesale)
- **ACM/IEEE papers** — Check author's postprint policy; authors often allow redistribution
- **University-hosted theses** — Often available under fair use

**⚠ Do not use:**
- ACM/IEEE paywalled journals without author permission
- Springer or Elsevier paywalled content
- Course materials marked "proprietary" or "restricted"

---

## Auditing & Maintenance

### Quarterly Audit Checklist

```bash
# 1. Generate inventory
python -c "
from src.flashcards.tools.glossary_audit import GlossaryAudit
audit = GlossaryAudit()
summary = audit.summary()
print(f\"Total terms: {summary['total_terms']}\")
print(f\"By tier: {summary['by_tier']}\")
print(f\"Issues: {len(summary['compliance_issues'])} found\")
"

# 2. Export as CSV for review
python -c "
from pathlib import Path
from src.flashcards.tools.glossary_audit import GlossaryAudit
GlossaryAudit().export_csv(Path('glossary_audit.csv'))
"

# 3. Check for missing metadata
python -m src.flashcards.tools.glossary_audit --check-tiers
python -m src.flashcards.tools.glossary_audit --check-attribution

# 4. Verify all licenses are valid
# (Manual: scan CSV for misspelled licenses or missing URLs)
```

### Handling DMCA/Takedown Requests

1. **Immediate action:** Remove the glossary from the codebase
2. **Communicate:** File issue explaining which terms were removed and why
3. **Evaluate:** Consult legal counsel on fair use defense if the source disputes our claim
4. **Republish:** If fair use is defensible, republish with stronger documentation

---

## Adding Glossaries: Checklist

- [ ] Source classified as Tier 1, 2, or 3
- [ ] All fields in metadata template completed
- [ ] Fair use justification included (Tier 2 only)
- [ ] Compliance audit passes: `python -m src.flashcards.tools.glossary_audit --check-tiers`
- [ ] Attribution audit passes: `python -m src.flashcards.tools.glossary_audit --check-attribution`
- [ ] PR includes rationale for Tier 2 sources
- [ ] Maintainer review confirms classification

---

## FAQ

**Q: Can we use Stack Overflow answers?**  
A: No. Stack Overflow's ToS explicitly forbid scraping, and content is CC-BY-SA but requires visible attribution on the original site. Use fair-use-justifiable sources instead.

**Q: What if the author gives permission?**  
A: Excellent! Update metadata to `license: "custom"` and `notes: "Permission granted by [author] via email [date]"`. Link to the permission or keep a record.

**Q: Are we OK to commercialize Tier 2 glossaries?**  
A: Not without re-licensing. If Flashcards becomes a paid product, restrict Tier 2 glossaries to non-paying users or remove them. Tier 1 glossaries are safe for commercial use if license terms allow it (CC-BY-4.0 does).

**Q: What about plagiarism detection?**  
A: Flashcard summaries are transformative and will not trigger plagiarism detection when used properly. However, don't copy definitions wholesale; paraphrase and adapt for flashcard format.

**Q: How do we handle license changes?**  
A: Quarterly audits catch when a source changes its license. If a source moves from CC-BY to proprietary, flag it as "needs review" and consider replacing with a Tier 1 alternative.

---

## See Also

- [ADR 0001: Glossary Fair Use](adr/0001-glossary-fair-use.md) — Detailed decision record
- [Audit Tool](../src/flashcards/tools/glossary_audit.py) — Python implementation
- [Sample Glossaries](../data/raw_glossaries/) — Real examples with proper metadata
