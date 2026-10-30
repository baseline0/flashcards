"""Root test configuration: the tier marker comes from the folder a test lives in.

Every test file sits in one of the tier folders (unit/, integration/, contract/, host/, e2e/). This conftest adds the
matching marker at collection time, so `pytest -m unit` selects tests/unit/ and the other tiers likewise. Test authors
do not write tier markers by hand: a hand-written tier marker, or a test file at the top of tests/, fails collection.
"""

import os
from pathlib import Path

import pytest

TESTS_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
TIERS = ("unit", "integration", "contract", "host", "e2e")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Add each test's tier marker from its folder; refuse a test outside a tier folder or a hand-written tier marker."""
    for item in items:
        path = Path(item.path)
        if not path.is_relative_to(TESTS_ROOT):
            continue
        parts = path.relative_to(TESTS_ROOT).parts
        if len(parts) == 1 or parts[0] not in TIERS:
            raise pytest.UsageError(f"{item.nodeid}: move this test into one of the tier folders: {', '.join(TIERS)}")
        if any(item.get_closest_marker(name) for name in TIERS):
            raise pytest.UsageError(f"{item.nodeid}: do not declare a tier marker by hand; the folder sets the tier")
        item.add_marker(getattr(pytest.mark, parts[0]))
