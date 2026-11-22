#!/usr/bin/env python3
"""Check catalog.json, template packages, and vendored skill copies."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_lib import ROOT, read_catalog, validate_repository  # noqa: E402
from self_test import run_self_test  # noqa: E402


def main() -> int:
    failures = run_self_test()
    if failures:
        for item in failures:
            print(f"self-test error: {item}", file=sys.stderr)
        return 1
    problems = validate_repository(ROOT)
    if problems:
        for item in problems:
            print(f"error: {item}", file=sys.stderr)
        print(f"{len(problems)} error(s)", file=sys.stderr)
        return 1
    catalog, _load_problems = read_catalog(ROOT)
    templates = len(catalog["templates"]) if catalog else 0
    skills = len(catalog["skills"]) if catalog else 0
    print(f"ok: {templates} template(s), {skills} skill(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
