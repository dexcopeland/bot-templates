# Other platforms

Use the files in this folder on any host that accepts a system prompt plus skill or knowledge files. Install `skills/example-checklist/` from this template.

## Shared mapping

- System prompt or custom instructions: `persona.md`, then `scope.md`.
- Skill or knowledge files: `skills/example-checklist/SKILL.md` and `skills/example-checklist/references/format.md`.
- Tools: `tools.md`. This sample needs none.
- Schedule: the optional routine in `routines.md`, if the host has schedules.
- Trial prompts: `prompts.md`.

## Claude Projects

Put `persona.md` and `scope.md` in the project instructions. Add the skill folder to project knowledge.

## ChatGPT custom GPTs

Put `persona.md` and `scope.md` in the instructions. Upload `SKILL.md` and `references/format.md` as knowledge files.

## Cursor

Put `persona.md` and `scope.md` in a project rule or in `AGENTS.md` for a workspace used for this bot. Copy `skills/example-checklist/` into the project skill directory that Cursor setup already uses.

## Claude Code

Put `persona.md` and `scope.md` in `CLAUDE.md`. Copy `skills/example-checklist/` to the project skill directory, usually `.claude/skills/example-checklist/`. If that product's current docs name a different skill folder, use that folder.

## Generic system-prompt agents

Send `persona.md` and `scope.md` as the system message. Include the skill files in the same context, or load the skill folder as that host's skill bundle.
