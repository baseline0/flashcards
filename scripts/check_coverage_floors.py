"""Fail when a module's line coverage falls below its floor in pyproject.toml.

Reads the JSON report from `coverage json`. Floors live under [tool.flashcards.coverage_floors] and are a ratchet:
raise a floor when coverage rises, never lower one to make a change pass. Modules without a floor are reported but
not enforced.
"""

import json
import sys
import tomllib
from pathlib import Path

REPORT = Path(".coverage.json")
PYPROJECT = Path("pyproject.toml")
PREFIX = "src/flashcards/"


def main() -> int:
    floors: dict[str, float] = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["tool"]["flashcards"][
        "coverage_floors"
    ]
    files = json.loads(REPORT.read_text(encoding="utf-8"))["files"]
    measured = {path.removeprefix(PREFIX): data["summary"]["percent_covered"] for path, data in files.items()}

    failures = []
    for module, floor in sorted(floors.items()):
        if module not in measured:
            failures.append(f"{module}: not in the coverage report")
        elif measured[module] < floor:
            failures.append(f"{module}: {measured[module]:.1f}% is below its floor of {floor}%")
    if failures:
        print("coverage floors breached:")
        print("\n".join(f"  {line}" for line in failures))
        return 1
    print(f"coverage floors held for {len(floors)} modules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
