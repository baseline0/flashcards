"""Integration test configuration.

Every test under tests/integration/ gets the `integration` marker from the root
tests/conftest.py, so `pytest -m integration` selects this folder. Integration tests
may need sibling repos, local services, or cross-package contracts.
"""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: test requiring sibling repos or local setup")
