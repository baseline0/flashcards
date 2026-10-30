"""Unit test configuration.

Every test under tests/unit/ gets the `unit` marker from the root tests/conftest.py,
so `pytest -m unit` selects this folder. Unit tests are deterministic and need no
external services, network access, or sibling repos.
"""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: deterministic, isolated, no external dependencies")
