"""Tests for glossary ingestion metrics."""

import json
import tempfile
from pathlib import Path

from src.flashcards.domains.schemas import GlossaryEntry
from src.flashcards.metrics import GlossaryMetricsTracker


def test_update_ingestion_metrics():
    """Update metrics after ingesting entries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = GlossaryMetricsTracker(Path(tmpdir) / "metrics.json")

        # Create mock entries
        entries = [
            GlossaryEntry(
                id="1",
                domain="insurance",
                category="underwriting",
                title="Policy",
                body="Contract of insurance",
                metadata={},
            ),
            GlossaryEntry(
                id="2",
                domain="insurance",
                category="underwriting",
                title="Premium",
                body="Amount paid for insurance",
                metadata={},
            ),
        ]

        # Update metrics
        metrics = tracker.update_ingestion_metrics(
            entries, domain="insurance", total_available=10
        )

        assert metrics["by_domain"]["insurance"]["ingested"] == 2
        assert metrics["by_domain"]["insurance"]["available"] == 10
        assert metrics["total_ingested"] == 2
        assert metrics["total_available"] == 10
        assert metrics["completion_pct"] == 20.0


def test_metrics_file_created():
    """Metrics file is created after update."""
    with tempfile.TemporaryDirectory() as tmpdir:
        metrics_file = Path(tmpdir) / "metrics.json"
        tracker = GlossaryMetricsTracker(metrics_file)

        entries = [
            GlossaryEntry(
                id="1",
                domain="test",
                category="test",
                title="Term",
                body="Definition",
                metadata={},
            )
        ]

        tracker.update_ingestion_metrics(entries, "test", total_available=1)

        assert metrics_file.exists()
        data = json.loads(metrics_file.read_text())
        assert data["total_ingested"] == 1


def test_multiple_domains():
    """Track metrics across multiple domains."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = GlossaryMetricsTracker(Path(tmpdir) / "metrics.json")

        # Add insurance entries
        insurance_entries = [
            GlossaryEntry(
                id=str(i),
                domain="insurance",
                category="test",
                title=f"Term {i}",
                body="Definition",
                metadata={},
            )
            for i in range(5)
        ]
        tracker.update_ingestion_metrics(
            insurance_entries, "insurance", total_available=10
        )

        # Add AWS entries
        aws_entries = [
            GlossaryEntry(
                id=str(i),
                domain="aws",
                category="test",
                title=f"Service {i}",
                body="Definition",
                metadata={},
            )
            for i in range(3)
        ]
        tracker.update_ingestion_metrics(aws_entries, "aws", total_available=20)

        # Verify aggregation
        metrics = tracker.get_metrics()
        assert metrics["total_ingested"] == 8  # 5 + 3
        assert metrics["total_available"] == 30  # 10 + 20
        assert metrics["completion_pct"] == pytest.approx(26.67, abs=0.1)


def test_domain_progress():
    """Get progress for specific domain."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = GlossaryMetricsTracker(Path(tmpdir) / "metrics.json")

        entries = [
            GlossaryEntry(
                id=str(i),
                domain="finance",
                category="test",
                title=f"Term {i}",
                body="Definition",
                metadata={},
            )
            for i in range(7)
        ]
        tracker.update_ingestion_metrics(entries, "finance", total_available=14)

        progress = tracker.get_domain_progress("finance")

        assert progress is not None
        assert progress["ingested"] == 7
        assert progress["available"] == 14
        assert progress["completion_pct"] == 50.0


def test_progress_bar_formatting():
    """Progress bar formats correctly."""
    tracker = GlossaryMetricsTracker()

    bar_0 = tracker._progress_bar(0, width=10)
    assert "0.0%" in bar_0

    bar_50 = tracker._progress_bar(50, width=10)
    assert "50.0%" in bar_50

    bar_100 = tracker._progress_bar(100, width=10)
    assert "100.0%" in bar_100


def test_dashboard_formatting():
    """Format for dashboard produces human-readable output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = GlossaryMetricsTracker(Path(tmpdir) / "metrics.json")

        entries = [
            GlossaryEntry(
                id=str(i),
                domain="test",
                category="test",
                title=f"Term {i}",
                body="Definition",
                metadata={},
            )
            for i in range(3)
        ]
        tracker.update_ingestion_metrics(entries, "test", total_available=10)

        dashboard_fmt = tracker.format_for_dashboard()

        assert "title" in dashboard_fmt
        assert "overall" in dashboard_fmt
        assert "by_domain" in dashboard_fmt
        assert dashboard_fmt["overall"]["pct"] == "30.0%"
        assert "test" in [d["name"] for d in dashboard_fmt["by_domain"]]


def test_overall_progress():
    """Get overall progress summary."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = GlossaryMetricsTracker(Path(tmpdir) / "metrics.json")

        for domain in ["domain1", "domain2"]:
            entries = [
                GlossaryEntry(
                    id=str(i),
                    domain=domain,
                    category="test",
                    title=f"Term {i}",
                    body="Definition",
                    metadata={},
                )
                for i in range(2)
            ]
            tracker.update_ingestion_metrics(entries, domain, total_available=5)

        progress = tracker.get_overall_progress()

        assert progress["total_ingested"] == 4
        assert progress["total_available"] == 10
        assert progress["domains_tracked"] == 2


# Import pytest for approx
import pytest
