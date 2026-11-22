# Skills

Each folder here is one skill in the [Agent Skills](https://agentskills.io/specification) format: `SKILL.md` with `name` and `description` frontmatter, plus helper files next to it.

This directory is the canonical copy. Authors edit skills here, then run `python3 scripts/sync_skills.py` so every template that lists the skill gets the same files under `templates/<domain>/<template-id>/skills/<skill-id>/`.

Install a bot from the template folder. That folder already contains the skill copies it needs.

This tree is self-contained. A skill folder does not reference files outside itself, so `skills/` can move later into a plugin marketplace repo without rewriting skill text.
