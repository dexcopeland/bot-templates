# Grok Bot setup

Create a bot in Grok Bot and fill it from this folder.

1. Create a bot.
2. Name: {{Template Name}}.
3. Description / persona instructions: paste `persona.md`, then `scope.md`.
4. Skills: add each skill folder under `skills/`. Skip `skills/README.md`. Each skill folder contains `SKILL.md`.
5. Routines: add a routine only when `routines.md` describes one.
6. Connectors: connect the capabilities listed in `tools.md`.
7. Try a prompt from `prompts.md`.

| Grok Bot field | Source in this folder |
| --- | --- |
| Name | `template.json` field `name` |
| Description / persona | `persona.md` and `scope.md` |
| Skills | `skills/<skill-id>/` |
| Routines | `routines.md` |
| Connectors | `tools.md` |
