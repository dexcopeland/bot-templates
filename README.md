# Bot templates

Domain-specific bot templates and skills shared by Dex Copeland for personal projects and GRC (governance, risk, and compliance) work.

Each template is a package for Grok Bot, the desktop assistant where a bot has a name, persona instructions, skills, and optional routines and connectors. The same package is a persona and skill bundle for other agent hosts.

This repository includes one sample template and one sample skill so the layout is visible. Both are marked EXAMPLE. They show the format.

## Install a template in Grok Bot

1. Choose a template in [catalog.json](catalog.json). Note its `path`.
2. Open that folder. It holds the persona, the skills, and the setup notes.
3. Follow `grok-bot.md` in that folder.

The sample is [templates/example/example-assistant](templates/example/example-assistant/README.md).

## Install a template on another host

Follow `other-platforms.md` in the template folder. Persona, scope, tools, routines, prompts, and skills are written so a host can use them from the template folder alone.

## Repository layout

Templates are grouped by domain:

```text
templates/<domain>/<template-id>/
```

That folder is the whole bot. The skills it uses are copied into `templates/<domain>/<template-id>/skills/`. Copy the folder and you have the package.

`skills/<skill-id>/` at the repository root is the canonical copy of each skill. Authors edit that copy. `python3 scripts/sync_skills.py` refreshes the copies inside templates. Root `skills/` is also the tree to lift out later if these skills move to a plugin marketplace. Installing a template uses the nested copy.

`catalog.json` lists every template and skill with an id, a one-line description, domain tags, and the skills each template uses. [catalog.schema.json](catalog.schema.json) is the shape. [scripts/validate.py](scripts/validate.py) checks it.

`skeletons/` holds a blank template and a blank skill.

Suggested domains are `grc`, `productivity`, `writing`, and `career`. The `example` domain is reserved for samples. A template lives in one domain folder. Its `domain` field matches that folder and is the first entry in `domains`. Add further tags in `domains` when a template fits more than one area.

Domain folders keep a GRC template next to other GRC templates, and the path is predictable from the catalog: `templates/<domain>/<id>/`. Skills stay in one flat directory so the folder can move to another repo without rewriting paths inside skill files.

## Keep skill copies aligned

Edit a skill only under `skills/<skill-id>/`. Then run:

```bash
python3 scripts/sync_skills.py
python3 scripts/validate.py
```

Validation fails if a template names a missing skill, if a vendored copy differs from the canonical skill, or if `catalog.json` does not match the folders. GitHub Actions runs the same check.

Authoring steps are in [CONTRIBUTING.md](CONTRIBUTING.md). An agent installing from this repository should start at [AGENTS.md](AGENTS.md) or [llms.txt](llms.txt).

## License

MIT. See [LICENSE](LICENSE).
