#!/usr/bin/env python3
"""Copy canonical skills into the templates that list them.

`skills/<id>/` is the source of truth. This writes each listed skill into
`templates/<domain>/<template-id>/skills/<id>/` and removes vendored skill
folders that a template no longer lists.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_lib import ROOT, sync_repository  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync canonical skills into template packages.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift and leave files unchanged",
    )
    args = parser.parse_args()
    problems, actions = sync_repository(ROOT, write=not args.check)
    for action in actions:
        print(action)
    if problems:
        for item in problems:
            print(f"error: {item}", file=sys.stderr)
        print(f"{len(problems)} error(s)", file=sys.stderr)
        return 1
    if args.check:
        print("ok")
    elif not actions:
        print("skill copies already match")
    return 0


if __name__ == "__main__":
    sys.exit(main())
