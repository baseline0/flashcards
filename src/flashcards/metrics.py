"""Glossary ingestion metrics tracking for dashboard progress.

Tracks ingestion completeness: which domains have how many terms,
what % complete, and updates after each import.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class GlossaryMetricsTracker:
    """Track glossary ingestion progress by domain."""

    def __init__(self, metrics_file: Path = Path("results/glossary-metrics.json")):
        """Initialize tracker with metrics file path."""
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

    def update_ingestion_metrics(
        self,
        ingested_entries: list[Any],
        domain: str,
        total_available: int | None = None,
    ) -> dict:
        """Update metrics after ingesting entries.

        Args:
            ingested_entries: List of freshly ingested GlossaryEntry objects
            domain: Domain name (e.g., "insurance", "aws", "databricks")
            total_available: Total expected terms in domain (for % calculation)
                If None, uses current ingested count as total_available

        Returns:
            Updated metrics dict
        """
        # Load existing metrics
        metrics = self._load_metrics()

        # Initialize domain if new
        if domain not in metrics["by_domain"]:
            metrics["by_domain"][domain] = {
                "ingested": 0,
                "available": total_available or len(ingested_entries),
                "last_updated": None,
            }

        # Update domain metrics
        domain_metrics = metrics["by_domain"][domain]
        domain_metrics["ingested"] = len(ingested_entries)
        if total_available is not None:
            domain_metrics["available"] = total_available
        domain_metrics["last_updated"] = datetime.now().isoformat()

        # Recalculate totals
        total_ingested = sum(d["ingested"] for d in metrics["by_domain"].values())
        total_available = sum(d["available"] for d in metrics["by_domain"].values())

        metrics["total_ingested"] = total_ingested
        metrics["total_available"] = total_available
        metrics["completion_pct"] = (
            (total_ingested / total_available * 100)
            if total_available > 0
            else 0.0
        )
        metrics["timestamp"] = datetime.now().isoformat()

        # Save updated metrics
        self._save_metrics(metrics)

        return metrics

    def get_metrics(self) -> dict:
        """Get current ingestion metrics."""
        return self._load_metrics()

    def get_domain_progress(self, domain: str) -> dict | None:
        """Get progress for a specific domain.

        Returns:
            Dict with ingested, available, pct_complete; or None if not found
        """
        metrics = self._load_metrics()
        if domain not in metrics["by_domain"]:
            return None

        domain_data = metrics["by_domain"][domain]
        pct = (
            (domain_data["ingested"] / domain_data["available"] * 100)
            if domain_data["available"] > 0
            else 0.0
        )

        return {
            "domain": domain,
            "ingested": domain_data["ingested"],
            "available": domain_data["available"],
            "completion_pct": pct,
            "last_updated": domain_data["last_updated"],
        }

    def get_overall_progress(self) -> dict:
        """Get fleet-wide ingestion progress."""
        metrics = self._load_metrics()
        return {
            "total_ingested": metrics["total_ingested"],
            "total_available": metrics["total_available"],
            "completion_pct": metrics["completion_pct"],
            "domains_tracked": len(metrics["by_domain"]),
            "domains": metrics["by_domain"],
            "timestamp": metrics["timestamp"],
        }

    def format_for_dashboard(self) -> dict:
        """Format metrics for dashboard display.

        Returns JSON-serializable dict with human-readable format.
        """
        metrics = self._load_metrics()
        progress = self.get_overall_progress()

        domains_display = []
        for domain, data in metrics["by_domain"].items():
            pct = (
                (data["ingested"] / data["available"] * 100)
                if data["available"] > 0
                else 0.0
            )
            domains_display.append({
                "name": domain,
                "status": f"{data['ingested']}/{data['available']}",
                "pct": f"{pct:.1f}%",
                "bar": self._progress_bar(pct, width=20),
            })

        return {
            "title": "Glossary Ingestion Progress",
            "overall": {
                "ingested": progress["total_ingested"],
                "available": progress["total_available"],
                "pct": f"{progress['completion_pct']:.1f}%",
                "bar": self._progress_bar(progress["completion_pct"], width=30),
            },
            "by_domain": domains_display,
            "timestamp": metrics["timestamp"],
        }

    def _load_metrics(self) -> dict:
        """Load metrics from file, or return empty structure."""
        if self.metrics_file.exists():
            try:
                return json.loads(self.metrics_file.read_text())
            except (json.JSONDecodeError, IOError):
                pass

        return {
            "timestamp": datetime.now().isoformat(),
            "total_ingested": 0,
            "total_available": 0,
            "completion_pct": 0.0,
            "by_domain": {},
        }

    def _save_metrics(self, metrics: dict) -> None:
        """Save metrics to file."""
        self.metrics_file.write_text(json.dumps(metrics, indent=2))

    @staticmethod
    def _progress_bar(pct: float, width: int = 20) -> str:
        """Generate ASCII progress bar."""
        filled = int(width * pct / 100)
        empty = width - filled
        return f"[{'=' * filled}{'-' * empty}] {pct:.1f}%"
