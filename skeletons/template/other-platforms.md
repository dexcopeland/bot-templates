# Other platforms

Install the skill folders inside this template. The shared mapping below is the same for each host.

## Shared mapping

- System prompt or custom instructions: `persona.md`, then `scope.md`.
- Skill or knowledge files: each `skills/<skill-id>/` folder, starting from `SKILL.md` and the relative files it links.
- Tools: `tools.md`.
- Schedule: `routines.md`, if the host has schedules and the file describes one.
- Trial prompts: `prompts.md`.

## Claude Projects

Put `persona.md` and `scope.md` in the project instructions. Add each skill folder to project knowledge.

## ChatGPT custom GPTs

Put `persona.md` and `scope.md` in the instructions. Upload each skill's `SKILL.md` and linked helper files as knowledge.

## Cursor

Put `persona.md` and `scope.md` in a project rule or in `AGENTS.md` for a workspace used for this bot. Copy each `skills/<skill-id>/` folder into the project skill directory that Cursor setup already uses.

## Claude Code

Put `persona.md` and `scope.md` in `CLAUDE.md`. Copy each `skills/<skill-id>/` folder to the project skill directory, usually `.claude/skills/<skill-id>/`. If that product's current docs name a different skill folder, use that folder.

## Generic system-prompt agents

Send `persona.md` and `scope.md` as the system message. Include the skill files in the same context, or load each skill folder as that host's skill bundle.
