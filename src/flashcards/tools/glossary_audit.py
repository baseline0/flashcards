"""Tools for auditing glossary sources and compliance."""

import json
import csv
from pathlib import Path
from typing import Any
from collections import defaultdict

from ..core.config import settings


class GlossaryAudit:
    """Audit glossary sources for compliance and licensing."""

    def __init__(self, glossaries_path: Path = settings.glossaries_path):
        self.glossaries_path = glossaries_path

    def inventory(self) -> list[dict[str, Any]]:
        """Generate an inventory of all glossaries and their sources."""
        items = []

        for domain_path in self.glossaries_path.iterdir():
            if not domain_path.is_dir():
                continue

            for glossary_file in domain_path.glob("*.json"):
                try:
                    with open(glossary_file) as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    continue

                if not isinstance(data, list):
                    data = [data]

                for entry in data:
                    metadata = entry.get("metadata", {})
                    items.append({
                        "domain": domain_path.name,
                        "glossary": glossary_file.stem,
                        "term": entry.get("title", ""),
                        "source_url": metadata.get("source_url", ""),
                        "source_name": metadata.get("source_name", ""),
                        "license": metadata.get("license", "unknown"),
                        "tier": metadata.get("tier", 0),
                        "attribution_required": metadata.get("attribution_required", False),
                        "commercial_use": metadata.get("commercial_use", False),
                        "scraped_date": metadata.get("scraped_date", ""),
                        "fair_use": bool(metadata.get("fair_use_justification")),
                    })

        return items

    def summary(self) -> dict[str, Any]:
        """Generate compliance summary by domain and tier."""
        items = self.inventory()
        summary = {
            "total_terms": len(items),
            "by_domain": defaultdict(lambda: defaultdict(int)),
            "by_license": defaultdict(int),
            "by_tier": defaultdict(int),
            "compliance_issues": [],
        }

        for item in items:
            domain = item["domain"]
            tier = item["tier"]
            license_type = item["license"]

            summary["by_domain"][domain]["total"] += 1
            summary["by_domain"][domain][f"tier_{tier}"] += 1
            summary["by_license"][license_type] += 1
            summary["by_tier"][tier] += 1

            # Flag issues
            if tier == 0:
                summary["compliance_issues"].append(
                    f"{item['glossary']}: {item['term']} has no tier classification"
                )
            if item["commercial_use"] is False and not item.get("license"):
                summary["compliance_issues"].append(
                    f"{item['glossary']}: {item['term']} restricts commercial use but has no license"
                )

        return {
            "total_terms": summary["total_terms"],
            "by_domain": dict(summary["by_domain"]),
            "by_license": dict(summary["by_license"]),
            "by_tier": dict(summary["by_tier"]),
            "compliance_issues": summary["compliance_issues"],
        }

    def export_csv(self, output_path: Path) -> None:
        """Export inventory as CSV for auditing."""
        items = self.inventory()

        if not items:
            print("No glossaries found")
            return

        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=items[0].keys())
            writer.writeheader()
            writer.writerows(items)

        print(f"Exported {len(items)} terms to {output_path}")

    def check_tier_compliance(self) -> bool:
        """Verify all glossaries are properly classified (Tier 1, 2, or 3)."""
        items = self.inventory()
        issues = [item for item in items if item["tier"] == 0]

        if issues:
            print(f"⚠ {len(issues)} terms lack tier classification:")
            for issue in issues[:5]:
                print(f"  - {issue['glossary']}/{issue['term']}")
            return False

        print(f"✓ All {len(items)} terms are properly classified")
        return True

    def check_attribution(self) -> bool:
        """Verify all required attributions are present."""
        items = self.inventory()
        issues = [
            item for item in items
            if item["attribution_required"] and not item.get("source_name")
        ]

        if issues:
            print(f"⚠ {len(issues)} terms require attribution but lack source:")
            for issue in issues[:5]:
                print(f"  - {issue['glossary']}/{issue['term']}")
            return False

        print(f"✓ All required attributions are present")
        return True
