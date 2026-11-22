#!/usr/bin/env python3
"""Fixture checks for the catalog validator and skill sync."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_lib import (  # noqa: E402
    SKILL_FIELDS,
    TEMPLATE_FIELDS,
    sync_repository,
    validate_repository,
)


def write_schema(root: Path) -> None:
    schema = {
        "$defs": {
            "skill": {"required": list(SKILL_FIELDS)},
            "template": {"required": list(TEMPLATE_FIELDS)},
        }
    }
    (root / "catalog.schema.json").write_text(json.dumps(schema), encoding="utf-8")


def write_fixture(root: Path) -> None:
    skill = root / "skills" / "demo"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                "description: Demo skill used by the validator self-test.",
                "---",
                "",
                "# Demo",
                "",
                "EXAMPLE. Read [references/note.md](references/note.md).",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (skill / "references" / "note.md").write_text("# Note\n\nOne step.\n", encoding="utf-8")
    (root / "skills" / "README.md").write_text("# Skills\n", encoding="utf-8")

    template = root / "templates" / "example" / "demo-bot"
    (template / "skills").mkdir(parents=True)
    shutil.copytree(skill, template / "skills" / "demo")
    (template / "skills" / "README.md").write_text("Bundled copies.\n", encoding="utf-8")
    readme = "\n".join(
        [
            "# Demo Bot",
            "",
            "EXAMPLE. See persona.md, scope.md, tools.md, routines.md, prompts.md, grok-bot.md, and other-platforms.md.",
            "",
            "Skills live in skills/.",
            "",
        ]
    )
    (template / "README.md").write_text(readme, encoding="utf-8")
    for name, body in (
        ("persona.md", "You answer with a checklist.\n"),
        ("scope.md", "Stay on the checklist.\n"),
        ("tools.md", "No tools.\n"),
        ("routines.md", "No schedule.\n"),
        ("prompts.md", "Make a checklist for packing.\n"),
        ("grok-bot.md", "Grok Bot uses persona.md.\n"),
        ("other-platforms.md", "Claude uses persona.md.\n"),
    ):
        (template / name).write_text(body, encoding="utf-8")
    template_meta = {
        "id": "demo-bot",
        "name": "Demo Bot",
        "description": "Sample bot used by the validator self-test.",
        "domain": "example",
        "domains": ["example"],
        "skills": ["demo"],
        "example": True,
    }
    (template / "template.json").write_text(
        json.dumps(template_meta, indent=2) + "\n",
        encoding="utf-8",
    )
    catalog = {
        "$schema": "./catalog.schema.json",
        "version": 1,
        "skills": [
            {
                "id": "demo",
                "name": "Demo",
                "description": "Sample skill used by the validator self-test.",
                "domains": ["example"],
                "path": "skills/demo",
                "example": True,
            }
        ],
        "templates": [
            {
                **template_meta,
                "path": "templates/example/demo-bot",
            }
        ],
    }
    (root / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    write_schema(root)


def run_self_test() -> list[str]:
    problems: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_fixture(root)
        found = validate_repository(root)
        if found:
            return ["fixture should be valid, got: " + " | ".join(found)]

        nested = root / "templates" / "example" / "demo-bot" / "skills" / "demo" / "SKILL.md"
        nested.write_text(nested.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")
        found = validate_repository(root)
        if not any("does not match" in item for item in found):
            problems.append("fixture drift was not reported")

        sync_problems, actions = sync_repository(root, write=True)
        if sync_problems:
            problems.append("sync failed: " + " | ".join(sync_problems))
        if not any(item.startswith("copied ") for item in actions):
            problems.append("sync did not refresh the drifted skill")
        found = validate_repository(root)
        if found:
            problems.append("fixture should pass after sync, got: " + " | ".join(found))

        persona = root / "templates" / "example" / "demo-bot" / "persona.md"
        persona.write_text(persona.read_text(encoding="utf-8") + "Use Grok Bot.\n", encoding="utf-8")
        found = validate_repository(root)
        if not any("host product" in item for item in found):
            problems.append("a host product in persona.md was not reported")

        extra = root / "skills" / "demo" / "extra.md"
        extra.write_text("orphan\n", encoding="utf-8")
        found = validate_repository(root)
        if not any("extra.md" in item and "SKILL.md" in item for item in found):
            problems.append("an unlinked helper was not reported")
    return problems


if __name__ == "__main__":
    failures = run_self_test()
    if failures:
        for item in failures:
            print(item, file=sys.stderr)
        sys.exit(1)
    print("self-test ok")
