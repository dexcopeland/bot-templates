# Contributing

Add a skill under `skills/`, add a template under `templates/<domain>/<template-id>/`, list both in `catalog.json`, and sync the skill copies into the template.

The sample template and sample skill are marked EXAMPLE. New work uses `"example": false` and a domain other than `example`.

## Why templates are grouped by domain

People ask for a domain first: a GRC bot, a writing bot, a career bot. The path `templates/<domain>/<template-id>/` matches that, and it matches the catalog fields `domain` and `path`.

A template has one folder. `domain` is that folder name and the first item in `domains`. Extra items in `domains` are tags for search, such as a GRC template that also drafts prose: `"domain": "grc", "domains": ["grc", "writing"]`.

Suggested domains:

- `grc` for governance, risk, and compliance
- `productivity`
- `writing`
- `career`

Add a domain by creating `templates/<domain>/<template-id>/` for the first template in it. Reserve `example` for labeled samples.

Skills stay in a flat `skills/<skill-id>/` directory. They are cross-domain, and that directory is the unit to move if skills later become a plugin marketplace.

## Skill copies

A skill can appear in more than one place.

- Canonical copy: `skills/<skill-id>/`. Edit this one.
- Vendored copy: `templates/<domain>/<template-id>/skills/<skill-id>/`. This is what a user or agent installs. The template folder has to stand alone, so it carries the files.

`python3 scripts/sync_skills.py` copies each canonical skill into every template that lists it, and deletes vendored skill folders the template no longer lists. It leaves `templates/.../skills/README.md` in place.

`python3 scripts/sync_skills.py --check` reports drift and does not write. `python3 scripts/validate.py` includes that drift check, plus the catalog and file checks. CI runs both commands.

If you change a vendored copy, copy that change up to `skills/<skill-id>/` if you meant to keep it, then run the sync script. The next validation fails while the copies differ.

Templates do not read `skills/` at the repo root when someone installs them. After a sync, the nested copy matches.

## Add a skill

1. Copy `skeletons/skill/` to `skills/<skill-id>/`.
2. Replace every `{{token}}`.
3. `SKILL.md` starts with YAML frontmatter. Required keys are `name` and `description`, each on one line. `name` equals the folder name and uses lowercase letters, numbers, and hyphens.
4. Put helper files inside the skill folder. Link each one from `SKILL.md` with a relative path, for example `[references/notes.md](references/notes.md)`. Do not reference `../` outside the skill folder.
5. Add an object to `skills` in `catalog.json`. `path` must be `skills/<skill-id>`. `description` is one line, up to 200 characters. The frontmatter `description` can be longer (up to 1024 characters) and should say what the skill does and when to use it.
6. Run `python3 scripts/validate.py`.

Set `"example": true` only for a sample, and include `example` in `domains`. The `SKILL.md` body must contain the token `EXAMPLE`.

## Add a template

1. Copy `skeletons/template/` to `templates/<domain>/<template-id>/`.
2. Replace every `{{token}}` in the markdown files and in `template.json`.
3. Set `skills` to ids that already exist under `skills/`. Order in `template.json` must match the catalog entry.
4. Write the platform-neutral files without host product names. The validator rejects these names in `persona.md`, `scope.md`, `tools.md`, `routines.md`, and `prompts.md`: Grok, Claude, ChatGPT, OpenAI, Cursor, and GPT. Put host steps in `grok-bot.md` and `other-platforms.md`.
5. In `tools.md`, name capabilities (calendar read access, an editable notes document). Name the product in the host setup files.
6. In `routines.md`, describe any schedule in plain language.
7. Add an object to `templates` in `catalog.json`. `path` must be `templates/<domain>/<template-id>`. `domain` must match the folder and `domains[0]`. `id`, `name`, `description`, `domain`, `domains`, `skills`, and `example` must match `template.json`.
8. The template `README.md` must mention `persona.md`, `scope.md`, `tools.md`, `routines.md`, `prompts.md`, `grok-bot.md`, `other-platforms.md`, and `skills/`.
9. Run:

```bash
python3 scripts/sync_skills.py
python3 scripts/validate.py
```

Set `"example": true` only for a sample in the `example` domain. The template `README.md` must contain the token `EXAMPLE`.

## Catalog

`catalog.json` is the machine-readable index. `catalog.schema.json` documents it. `scripts/validate.py` enforces the same required fields without extra packages. Standard-library Python is enough.

Catalog skill fields: `id`, `name`, `description`, `domains`, `path`, `example`.

Catalog template fields: `id`, `name`, `description`, `domain`, `domains`, `path`, `skills`, `example`.

`version` is `1`.

## Template files

| File | Role |
| --- | --- |
| `template.json` | Id, name, description, domain, domains, skills, example flag |
| `README.md` | What the bot does and where to install it |
| `persona.md` | Platform-neutral system instructions |
| `scope.md` | In scope, out of scope, guardrails |
| `tools.md` | Tools and connectors as generic capabilities |
| `routines.md` | Suggested schedules in plain language |
| `prompts.md` | Example requests |
| `grok-bot.md` | Grok Bot field mapping |
| `other-platforms.md` | Mapping for other agent hosts |
| `skills/README.md` | Note that nested skills are vendored copies |
| `skills/<skill-id>/` | Skill files copied from `skills/<skill-id>/` |

## Checks

```bash
python3 scripts/validate.py
python3 scripts/sync_skills.py --check
```

`validate.py` also runs a small self-test of the drift and file checks before it reads this repository.
