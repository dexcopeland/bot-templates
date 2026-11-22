# Grok Bot setup

Create a bot in Grok Bot and fill it from this folder. Attach `skills/example-checklist/`, including `SKILL.md` and `references/format.md`.

1. Create a bot.
2. Name: Example Assistant.
3. Description / persona instructions: paste `persona.md`, then `scope.md`.
4. Skills: add the `skills/example-checklist` folder from this template.
5. Routines: optional. If you add one, use the weekly routine in `routines.md`.
6. Connectors: none. See `tools.md`.
7. Try a prompt from `prompts.md`.

| Grok Bot field | Source in this folder |
| --- | --- |
| Name | `template.json` field `name` |
| Description / persona | `persona.md` and `scope.md` |
| Skills | `skills/<skill-id>/` |
| Routines | `routines.md`, only if you want a schedule |
| Connectors | `tools.md` |
