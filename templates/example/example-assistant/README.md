# Example Assistant

EXAMPLE. This template shows the package layout. It is a sample of the format. It is not a bot Dex Copeland uses for real work.

## What it does

Example Assistant takes one short request and answers with a three-item checklist. It follows the `example-checklist` skill bundled in `skills/example-checklist/`.

## Files

- `template.json` holds the id, description, domain tags, and skill ids.
- `persona.md` is the system instructions.
- `scope.md` is what the bot will and will not do.
- `tools.md` lists connector needs. This sample needs none.
- `routines.md` describes an optional schedule in plain language.
- `prompts.md` has requests you can try.
- `grok-bot.md` maps those files onto Grok Bot.
- `other-platforms.md` maps those files onto other agent hosts.
- `skills/` holds the skill copies for this bot.

## Install

This folder is the whole package. Use the skill in `skills/`. You can copy the folder out of the repository and still install the bot.

- Grok Bot: follow `grok-bot.md`.
- Another agent host: follow `other-platforms.md`.
