# Agent instructions

This repository publishes domain-specific bot templates and skills from Dex Copeland. A template is a persona, a skill bundle, guardrails, and setup notes for one bot.

Grok Bot is the primary host. The same folder can be installed as a persona on Claude Projects, ChatGPT custom GPTs, Cursor, Claude Code, or any system-prompt agent.

Entries with `"example": true` are samples of the layout. Use one only when the user asked for the example or for a sample of this format.

## Find a template

1. Read `catalog.json` at the repository root. In a checkout, read the local file. To fetch the default branch without cloning, start at `https://raw.githubusercontent.com/dexcopeland/bot-templates/main/catalog.json`. Other files are that same prefix plus a repo path, such as `templates/example/example-assistant/persona.md` or `templates/example/example-assistant/skills/example-checklist/SKILL.md`.
2. Choose an entry in `templates` by `id`, `description`, `domain`, or `domains`.
3. Open `path`. It is always `templates/<domain>/<id>/`.

If the user names a skill, read `skills` in `catalog.json`. `path` there is the canonical skill for authors. To install a skill as part of a bot, use a template that lists that skill, and read the copy inside the template.

## Install a template

The template directory is complete. Read skills from `<template>/skills/`.

1. Read `template.json` for `name`, `description`, `skills`, and `example`.
2. Read `README.md` in the template.
3. Read `persona.md`, `scope.md`, `tools.md`, `routines.md`, and `prompts.md`.
4. For each id in `template.json` `skills`, read `skills/<id>/SKILL.md`. Then read every relative file that `SKILL.md` links. Those links cover the helper files in the skill folder.
5. For Grok Bot, follow `grok-bot.md`.
6. For any other host, follow `other-platforms.md`.

`persona.md`, `scope.md`, `tools.md`, `routines.md`, and `prompts.md` describe the bot without naming a host product. Host steps stay in `grok-bot.md` and `other-platforms.md`.

## Layout

```text
catalog.json                          index of templates and skills
catalog.schema.json                   shape of catalog.json
AGENTS.md                             this file
llms.txt                              short map for agents
CONTRIBUTING.md                       authoring rules and the sync rule
skills/<skill-id>/SKILL.md            canonical skill
skills/<skill-id>/...                 helper files linked from SKILL.md
templates/<domain>/<template-id>/     one self-contained bot package
  template.json
  README.md
  persona.md
  scope.md
  tools.md
  routines.md
  prompts.md
  grok-bot.md
  other-platforms.md
  skills/README.md
  skills/<skill-id>/                  copy of the canonical skill
skeletons/skill/                      blank skill to copy
skeletons/template/                   blank template to copy
scripts/validate.py                   catalog, files, and drift check
scripts/sync_skills.py                refresh vendored skills from skills/
```

Suggested template domains are `grc`, `productivity`, `writing`, and `career`. `example` is reserved for samples.

## Authors

Edit a skill only in `skills/<id>/`. Run `python3 scripts/sync_skills.py` before you commit. `python3 scripts/validate.py` checks the catalog, the required files, and that vendored skills match the canonical copies.

The root `skills/` tree can move later to a plugin marketplace. Skill folders do not point at files outside themselves. Templates do not load skills from the root tree at install time.
