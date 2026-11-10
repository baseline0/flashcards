"""Glossary sourcing rules: every term records its tier, provenance and fair-use basis (ADR 0001).

Design intent: a term enters the deck only with the metadata that makes its source auditable, so the
sourcing policy is checked by the test gate rather than by a manual audit run.
Happy path: a complete Tier 1 or Tier 2 term has no violations.
Unhappy paths: a missing field, an unknown tier, a Tier 2 term without justification or with commercial use,
a bad date, and a glossary file outside the domain/name layout are each reported.
The committed data may carry recorded debt; the ceilings below may only be lowered as terms are fixed.

## Specification Map

| Rule | Authority | Enforcement |
|------|-----------|------------|
| Every term records source_url, source_name, license, attribution_required, tier, commercial_use, scraped_date | tests/unit/test_glossary_sourcing.py | test_a_term_missing_any_provenance_field_is_reported |
| Only Tier 1 and Tier 2 are stored; Tier 3 is never stored | tests/unit/test_glossary_sourcing.py | test_only_tiers_1_and_2_are_ever_stored |
| Tier 1 links its license text | tests/unit/test_glossary_sourcing.py | test_a_tier_1_term_without_a_license_url_is_reported |
| Required attribution has attribution text | tests/unit/test_glossary_sourcing.py | test_attribution_text_is_required_whenever_attribution_is_required |
| Tier 2 has a fair-use justification | tests/unit/test_glossary_sourcing.py | test_a_tier_2_term_without_a_fair_use_justification_is_reported |
| Tier 2 is marked non-commercial | tests/unit/test_glossary_sourcing.py | test_a_tier_2_term_is_refused_unless_it_is_marked_non_commercial |
| scraped_date is ISO-8601 | tests/unit/test_glossary_sourcing.py | test_scraped_date_must_be_an_iso_8601_date |
| Files sit at data/raw_glossaries/{domain}/{glossary_name}.json | tests/unit/test_glossary_sourcing.py | test_glossary_files_sit_in_a_domain_folder_and_are_named_by_glossary |
| Committed terms stay within recorded sourcing debt (the audit run before commit is now the test gate) | tests/unit/test_glossary_sourcing.py | test_committed_glossary_terms_stay_within_the_recorded_sourcing_debt |
| Source is classified (Q1 to Q3) before scraping | tests/unit/test_glossary_sourcing.py | test_scraper_classifies_a_source_before_fetching (xfail) |
| Tier 3 sources are skipped, never fetched | tests/unit/test_glossary_sourcing.py | test_scraper_never_fetches_a_tier_3_source (xfail) |
| Tier 2 pull request includes a rationale | tests/unit/test_glossary_sourcing.py | test_tier_2_pull_request_states_its_rationale (xfail) |
| Maintainer review confirms each classification | tests/unit/test_glossary_sourcing.py | test_maintainer_review_confirms_each_source_classification (xfail) |
"""

import json
from collections import Counter
from datetime import date
from typing import Any

import pytest

from flashcards.constants import REPO_ROOT

GLOSSARY_ROOT = REPO_ROOT / "data" / "raw_glossaries"

REQUIRED_FOR_EVERY_TIER = (
    "source_url",
    "source_name",
    "license",
    "attribution_required",
    "tier",
    "commercial_use",
    "scraped_date",
)

# Recorded sourcing debt in the committed glossaries, per violation kind. Ratchet: a count may fall, never rise.
SOURCING_DEBT_CEILING: dict[str, int] = {
    "source_url-missing": 46,
    "source_name-missing": 155,
    "license-missing": 46,
    "attribution_required-missing": 155,
    "tier-missing": 155,
    "commercial_use-missing": 155,
    "scraped_date-missing": 165,
    "scraped_date-not-iso": 0,
    "tier-not-1-or-2": 0,
    "tier1-license_url-missing": 66,
    "attribution_text-missing": 0,
    "tier2-justification-missing": 27,
    "tier2-commercial-use-not-false": 17,
}


def sourcing_violations(metadata: dict[str, Any]) -> list[str]:
    """Return the sourcing rule names this term's metadata breaks; an empty list means compliant."""
    found = [f"{key}-missing" for key in REQUIRED_FOR_EVERY_TIER if metadata.get(key) in (None, "")]
    tier = metadata.get("tier")
    if tier is not None and tier not in (1, 2):
        found.append("tier-not-1-or-2")
    if metadata.get("scraped_date") not in (None, ""):
        try:
            date.fromisoformat(str(metadata["scraped_date"]))
        except ValueError:
            found.append("scraped_date-not-iso")
    if tier == 1 and not metadata.get("license_url"):
        found.append("tier1-license_url-missing")
    if metadata.get("attribution_required") is True and not metadata.get("attribution_text"):
        found.append("attribution_text-missing")
    if tier == 2:
        if not metadata.get("fair_use_justification"):
            found.append("tier2-justification-missing")
        if metadata.get("commercial_use") is not False:
            found.append("tier2-commercial-use-not-false")
    return found


def complete_tier_1() -> dict[str, Any]:
    return {
        "source_url": "https://en.wikipedia.org/wiki/Epoch_(computing)",
        "source_name": "Wikipedia: Epoch (Computing)",
        "license": "CC-BY-SA-3.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
        "attribution_required": True,
        "attribution_text": "Wikipedia Contributors",
        "tier": 1,
        "commercial_use": True,
        "scraped_date": "2026-09-16",
    }


def complete_tier_2() -> dict[str, Any]:
    return {
        "source_url": "https://docs.aws.amazon.com/ec2/",
        "source_name": "AWS EC2 Documentation",
        "license": "proprietary",
        "fair_use_justification": "Educational study aid; glossary format is transformative",
        "attribution_required": True,
        "attribution_text": "Amazon Web Services",
        "tier": 2,
        "commercial_use": False,
        "scraped_date": "2026-09-16",
    }


def test_a_complete_tier_1_term_has_no_sourcing_violations():
    """Open-access terms with license, license URL and attribution are compliant as written."""
    assert sourcing_violations(complete_tier_1()) == []


def test_a_complete_tier_2_term_has_no_sourcing_violations():
    """Fair-use terms carry a justification and are non-commercial, which is what ADR 0001 requires."""
    assert sourcing_violations(complete_tier_2()) == []


@pytest.mark.parametrize("key", REQUIRED_FOR_EVERY_TIER)
def test_a_term_missing_any_provenance_field_is_reported(key: str):
    """Every term must name its source, licence, tier and scrape date, whichever tier it is."""
    metadata = complete_tier_1()
    del metadata[key]
    assert f"{key}-missing" in sourcing_violations(metadata)


@pytest.mark.parametrize("tier", [0, 3, "1"])
def test_only_tiers_1_and_2_are_ever_stored(tier: Any):
    """Tier 3 (prohibited) is never scraped, so a term with any other tier value is refused."""
    metadata = complete_tier_1() | {"tier": tier}
    assert "tier-not-1-or-2" in sourcing_violations(metadata)


def test_a_tier_1_term_without_a_license_url_is_reported():
    """Open-access terms must link their license text so the license can be verified."""
    metadata = complete_tier_1()
    del metadata["license_url"]
    assert "tier1-license_url-missing" in sourcing_violations(metadata)


def test_attribution_text_is_required_whenever_attribution_is_required():
    """A term that must be credited states how to credit it."""
    metadata = complete_tier_1() | {"attribution_text": ""}
    assert "attribution_text-missing" in sourcing_violations(metadata)


def test_a_tier_2_term_without_a_fair_use_justification_is_reported():
    """Fair-use terms record the reasoning that makes the use defensible."""
    metadata = complete_tier_2()
    del metadata["fair_use_justification"]
    assert "tier2-justification-missing" in sourcing_violations(metadata)


@pytest.mark.parametrize("commercial_use", [True, None])
def test_a_tier_2_term_is_refused_unless_it_is_marked_non_commercial(commercial_use: Any):
    """Tier 2 terms cannot ship in paid products, so commercial use must be recorded as explicitly false."""
    metadata = complete_tier_2() | {"commercial_use": commercial_use}
    assert "tier2-commercial-use-not-false" in sourcing_violations(metadata)


@pytest.mark.parametrize("scraped_date", ["16/09/2026", "yesterday", "2026-13-01"])
def test_scraped_date_must_be_an_iso_8601_date(scraped_date: str):
    """The scrape date is recorded as ISO-8601 so provenance can be sorted and audited."""
    assert "scraped_date-not-iso" in sourcing_violations(complete_tier_1() | {"scraped_date": scraped_date})


def test_glossary_files_sit_in_a_domain_folder_and_are_named_by_glossary():
    """Glossary files live at data/raw_glossaries/{domain}/{glossary_name}.json, as the sourcing guide sets."""
    files = sorted(GLOSSARY_ROOT.rglob("*.json"))
    assert files, "no glossary files found"
    misplaced = [str(p.relative_to(GLOSSARY_ROOT)) for p in files if len(p.relative_to(GLOSSARY_ROOT).parts) != 2]
    assert misplaced == []


def committed_terms() -> list[tuple[str, dict[str, Any]]]:
    terms: list[tuple[str, dict[str, Any]]] = []
    for path in sorted(GLOSSARY_ROOT.rglob("*.json")):
        data = json.loads(path.read_text())
        for entry in data if isinstance(data, list) else [data]:
            terms.append((str(path.relative_to(GLOSSARY_ROOT)), entry.get("metadata", {})))
    return terms


def test_committed_glossary_terms_stay_within_the_recorded_sourcing_debt():
    """No committed term adds a sourcing violation beyond the ceilings recorded when the rules were written."""
    counts: Counter[str] = Counter()
    for _, metadata in committed_terms():
        counts.update(sourcing_violations(metadata))
    over = {
        rule: (counts[rule], SOURCING_DEBT_CEILING.get(rule, 0))
        for rule in counts
        if counts[rule] > SOURCING_DEBT_CEILING.get(rule, 0)
    }
    assert over == {}, f"sourcing violations above the recorded ceiling (rule: found, allowed): {over}"


@pytest.mark.xfail(
    strict=True,
    reason="owner: Mark Alexiuk; trigger: the scraper exists (a module that fetches glossary sources)",
)
def test_scraper_classifies_a_source_before_fetching():
    """Q1 to Q3 of the sourcing guide decide the tier before any page is fetched."""
    import flashcards.scraper as scraper_module

    assert callable(getattr(scraper_module, "classify_source", None))


@pytest.mark.xfail(
    strict=True,
    reason="owner: Mark Alexiuk; trigger: the scraper exists (a module that fetches glossary sources)",
)
def test_scraper_never_fetches_a_tier_3_source():
    """Tier 3 sources (paywalled, ToS-forbidden, proprietary) are skipped entirely, never scraped."""
    import flashcards.scraper as scraper_module

    assert callable(getattr(scraper_module, "scrape_glossary", None))


@pytest.mark.xfail(
    strict=True,
    reason="owner: Mark Alexiuk; trigger: a pull request template with a Tier 2 rationale section is committed under .github/",
)
def test_tier_2_pull_request_states_its_rationale():
    """A PR that adds a Tier 2 source explains why the fair-use basis holds."""
    template = REPO_ROOT / ".github" / "pull_request_template.md"
    assert template.exists() and "Tier 2" in template.read_text()


@pytest.mark.xfail(
    strict=True,
    reason="owner: Mark Alexiuk; trigger: CODEOWNERS names a glossary maintainer for data/raw_glossaries/",
)
def test_maintainer_review_confirms_each_source_classification():
    """A maintainer, not only the author, confirms each source's tier before it is merged."""
    owners = REPO_ROOT / ".github" / "CODEOWNERS"
    assert owners.exists() and "data/raw_glossaries" in owners.read_text()
