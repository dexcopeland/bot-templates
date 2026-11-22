#!/usr/bin/env python3
"""Catalog, template, and skill checks for the bot-templates repo.

Root `skills/<id>/` is the canonical skill. Each template vendors a copy at
`templates/<domain>/<template-id>/skills/<id>/`. Install from the template
copy. Edit the canonical skill, then sync.
"""

from __future__ import annotations

import filecmp
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ID_RE_SOURCE = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
MAX_ID_LEN = 64
MAX_NAME_LEN = 80
MAX_CATALOG_DESCRIPTION = 200
MAX_SKILL_DESCRIPTION = 1024

CATALOG_KEYS = {"$schema", "version", "skills", "templates"}
SKILL_FIELDS = ("id", "name", "description", "domains", "path", "example")
TEMPLATE_FIELDS = (
    "id",
    "name",
    "description",
    "domain",
    "domains",
    "path",
    "skills",
    "example",
)
TEMPLATE_JSON_FIELDS = (
    "id",
    "name",
    "description",
    "domain",
    "domains",
    "skills",
    "example",
)
TEMPLATE_FILES = (
    "README.md",
    "persona.md",
    "scope.md",
    "tools.md",
    "routines.md",
    "prompts.md",
    "grok-bot.md",
    "other-platforms.md",
    "template.json",
    "skills/README.md",
)
CORE_FILES = ("persona.md", "scope.md", "tools.md", "routines.md", "prompts.md")
README_MUST_MENTION = CORE_FILES + ("grok-bot.md", "other-platforms.md", "skills/")

ID_RE = re.compile(ID_RE_SOURCE)
PLATFORM_TERMS = re.compile(
    r"\b(Grok(?:\s+Bot)?|Claude(?:\s+Code)?|ChatGPT|OpenAI|Cursor|GPTs?)\b",
    re.IGNORECASE,
)
EXAMPLE_TOKEN = re.compile(r"\bEXAMPLE\b")
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
BACKTICK_PATH = re.compile(r"`([^`\n]+)`")


def skill_relpath(skill_id: str) -> str:
    return f"skills/{skill_id}"


def template_relpath(domain: str, template_id: str) -> str:
    return f"templates/{domain}/{template_id}"


def display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def safe_join(root: Path, relative: Path | str) -> Path:
    root_resolved = root.resolve()
    candidate = (root_resolved / relative).resolve()
    if candidate == root_resolved or root_resolved not in candidate.parents:
        raise RuntimeError(f"refusing to touch path outside the repository: {relative}")
    return candidate


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeError, OSError):
        return None


def read_catalog(root: Path) -> tuple[dict | None, list[str]]:
    path = root / "catalog.json"
    if not path.is_file():
        return None, ["catalog.json is missing"]
    text = read_text(path)
    if text is None:
        return None, ["catalog.json is not UTF-8 text"]
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, [f"catalog.json is not valid JSON ({exc})"]
    if not isinstance(data, dict):
        return None, ["catalog.json must be a JSON object"]
    return data, []


def check_id(value: object, label: str) -> list[str]:
    if not isinstance(value, str) or ID_RE.fullmatch(value) is None or len(value) > MAX_ID_LEN:
        return [f"{label} must be a kebab-case id of at most {MAX_ID_LEN} characters"]
    return []


def check_single_line(value: object, label: str, limit: int) -> list[str]:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\n" in value
        or "\r" in value
        or len(value) > limit
    ):
        return [f"{label} must be a single line of 1 to {limit} characters"]
    return []


def check_domains(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        return [f"{label} must be a non-empty list of domain ids"]
    problems: list[str] = []
    for index, item in enumerate(value):
        problems.extend(check_id(item, f"{label}[{index}]"))
    if len(value) != len(set(item for item in value if isinstance(item, str))):
        problems.append(f"{label} contains a duplicate domain")
    return problems


def check_exact_keys(entry: object, fields: tuple[str, ...], label: str) -> list[str]:
    if not isinstance(entry, dict):
        return [f"{label} must be an object"]
    missing = [key for key in fields if key not in entry]
    extra = sorted(set(entry) - set(fields))
    problems: list[str] = []
    if missing:
        problems.append(f"{label} is missing {', '.join(missing)}")
    if extra:
        problems.append(f"{label} has unknown fields {', '.join(extra)}")
    return problems


def check_catalog_shape(catalog: dict) -> list[str]:
    problems: list[str] = []
    extra = sorted(set(catalog) - CATALOG_KEYS)
    if extra:
        problems.append("catalog.json has unknown fields " + ", ".join(extra))
    if catalog.get("version") != 1:
        problems.append("catalog.json version must be 1")

    skills = catalog.get("skills")
    templates = catalog.get("templates")
    if not isinstance(skills, list):
        problems.append("catalog.json skills must be a list")
        skills = []
    if not isinstance(templates, list):
        problems.append("catalog.json templates must be a list")
        templates = []

    skill_ids: list[str] = []
    for index, entry in enumerate(skills):
        label = f"skills[{index}]"
        problems.extend(check_exact_keys(entry, SKILL_FIELDS, label))
        if not isinstance(entry, dict):
            continue
        problems.extend(check_id(entry.get("id"), f"{label}.id"))
        problems.extend(check_single_line(entry.get("name"), f"{label}.name", MAX_NAME_LEN))
        problems.extend(
            check_single_line(
                entry.get("description"),
                f"{label}.description",
                MAX_CATALOG_DESCRIPTION,
            )
        )
        problems.extend(check_domains(entry.get("domains"), f"{label}.domains"))
        if not isinstance(entry.get("example"), bool):
            problems.append(f"{label}.example must be a boolean")
        skill_id = entry.get("id")
        domains = entry.get("domains")
        if isinstance(skill_id, str) and ID_RE.fullmatch(skill_id):
            expected = skill_relpath(skill_id)
            if entry.get("path") != expected:
                problems.append(f"{label}.path must be {expected}")
            if skill_id in skill_ids:
                problems.append(f"duplicate skill id {skill_id}")
            skill_ids.append(skill_id)
        if isinstance(entry.get("example"), bool) and isinstance(domains, list):
            tagged = "example" in domains
            if entry["example"] and not tagged:
                problems.append(f"{label} is an example, so domains must include example")
            if tagged and entry["example"] is False:
                problems.append(f"{label} uses the example domain, so example must be true")

    known_skills = set(skill_ids)
    template_ids: list[str] = []
    for index, entry in enumerate(templates):
        label = f"templates[{index}]"
        problems.extend(check_exact_keys(entry, TEMPLATE_FIELDS, label))
        if not isinstance(entry, dict):
            continue
        problems.extend(check_id(entry.get("id"), f"{label}.id"))
        problems.extend(check_id(entry.get("domain"), f"{label}.domain"))
        problems.extend(check_single_line(entry.get("name"), f"{label}.name", MAX_NAME_LEN))
        problems.extend(
            check_single_line(
                entry.get("description"),
                f"{label}.description",
                MAX_CATALOG_DESCRIPTION,
            )
        )
        problems.extend(check_domains(entry.get("domains"), f"{label}.domains"))
        if not isinstance(entry.get("example"), bool):
            problems.append(f"{label}.example must be a boolean")
        domains = entry.get("domains")
        domain = entry.get("domain")
        if isinstance(domains, list) and domains and domain != domains[0]:
            problems.append(f"{label}.domain must match domains[0] and the folder name")
        template_id = entry.get("id")
        if (
            isinstance(template_id, str)
            and isinstance(domain, str)
            and ID_RE.fullmatch(template_id)
            and ID_RE.fullmatch(domain)
        ):
            expected = template_relpath(domain, template_id)
            if entry.get("path") != expected:
                problems.append(f"{label}.path must be {expected}")
            if template_id in template_ids:
                problems.append(f"duplicate template id {template_id}")
            template_ids.append(template_id)
        if isinstance(entry.get("example"), bool):
            if entry["example"] and domain != "example":
                problems.append(f"{label} is an example, so domain must be example")
            if domain == "example" and entry["example"] is False:
                problems.append(f"{label} uses the example domain, so example must be true")
        skill_list = entry.get("skills")
        if not isinstance(skill_list, list):
            problems.append(f"{label}.skills must be a list")
        else:
            seen_local: list[str] = []
            for skill_index, skill_id in enumerate(skill_list):
                problems.extend(check_id(skill_id, f"{label}.skills[{skill_index}]"))
                if isinstance(skill_id, str) and skill_id in seen_local:
                    problems.append(f"{label} lists skill {skill_id} more than once")
                if isinstance(skill_id, str):
                    seen_local.append(skill_id)
                    if skill_id not in known_skills:
                        problems.append(f"{label} lists unknown skill {skill_id}")
    return problems


def check_schema_file(root: Path) -> list[str]:
    path = root / "catalog.schema.json"
    if not path.is_file():
        return ["catalog.schema.json is missing"]
    text = read_text(path)
    if text is None:
        return ["catalog.schema.json is not UTF-8 text"]
    try:
        schema = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"catalog.schema.json is not valid JSON ({exc})"]
    try:
        skill_required = schema["$defs"]["skill"]["required"]
        template_required = schema["$defs"]["template"]["required"]
    except (KeyError, TypeError):
        return ["catalog.schema.json is missing $defs.skill.required or $defs.template.required"]
    problems: list[str] = []
    if set(skill_required) != set(SKILL_FIELDS):
        problems.append("catalog.schema.json skill.required does not match the validator")
    if set(template_required) != set(TEMPLATE_FIELDS):
        problems.append("catalog.schema.json template.required does not match the validator")
    return problems


def check_tree(root: Path, catalog: dict) -> list[str]:
    problems: list[str] = []
    skills_dir = root / "skills"
    templates_dir = root / "templates"
    if not skills_dir.is_dir():
        problems.append("skills/ is missing")
    if not templates_dir.is_dir():
        problems.append("templates/ is missing")
    if problems:
        return problems

    found_skills: set[str] = set()
    for child in skills_dir.iterdir():
        if child.name.startswith("."):
            continue
        if child.is_symlink():
            problems.append(f"skills/{child.name} is a symlink")
            continue
        if child.is_file():
            if child.name != "README.md":
                problems.append(f"skills/{child.name} is not a skill directory")
            continue
        if child.is_dir():
            found_skills.add(child.name)
            if not (child / "SKILL.md").is_file():
                problems.append(f"skills/{child.name}/SKILL.md is missing")
            continue
        problems.append(f"skills/{child.name} is not a skill directory")

    catalog_skills = {entry["id"] for entry in catalog["skills"]}
    for skill_id in sorted(found_skills - catalog_skills):
        problems.append(f"skills/{skill_id} is missing from catalog.json")
    for skill_id in sorted(catalog_skills - found_skills):
        problems.append(f"catalog.json lists {skill_id}, and skills/{skill_id} is missing")

    found_templates: set[str] = set()
    for domain_dir in templates_dir.iterdir():
        if domain_dir.name.startswith("."):
            continue
        relative_domain = f"templates/{domain_dir.name}"
        if domain_dir.is_symlink():
            problems.append(f"{relative_domain} is a symlink")
            continue
        if not domain_dir.is_dir():
            problems.append(f"{relative_domain} is not a domain directory")
            continue
        children = list(domain_dir.iterdir())
        if not children:
            problems.append(f"{relative_domain} is empty")
        for child in children:
            relative_template = f"{relative_domain}/{child.name}"
            if child.is_symlink():
                problems.append(f"{relative_template} is a symlink")
            elif child.is_dir():
                found_templates.add(relative_template)
            else:
                problems.append(f"{relative_template} is not a template directory")

    catalog_templates = {entry["path"] for entry in catalog["templates"]}
    for path in sorted(found_templates - catalog_templates):
        problems.append(f"{path} is missing from catalog.json")
    for path in sorted(catalog_templates - found_templates):
        problems.append(f"catalog.json lists {path}, and that directory is missing")
    return problems


def split_frontmatter(text: str) -> tuple[str, str] | None:
    if not text.startswith("---"):
        return None
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "".join(lines[1:index]), "".join(lines[index + 1 :])
    return None


def parse_frontmatter(text: str, label: str) -> tuple[dict[str, str] | None, str, list[str]]:
    parts = split_frontmatter(text)
    if parts is None:
        return None, "", [f"{label} must start with YAML frontmatter opened and closed by ---"]
    raw, body = parts
    data: dict[str, str] = {}
    problems: list[str] = []
    for line_no, line in enumerate(raw.splitlines(), start=2):
        if not line.strip():
            continue
        if line[:1].isspace():
            problems.append(f"{label} frontmatter values must be single-line (line {line_no})")
            continue
        if ":" not in line:
            problems.append(f"{label} has an invalid frontmatter line {line_no}")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key in data:
            problems.append(f"{label} repeats frontmatter key {key}")
            continue
        data[key] = value
    if problems:
        return None, body, problems
    return data, body, []


def extract_refs(text: str) -> set[str]:
    found: set[str] = set()
    for match in MARKDOWN_LINK.finditer(text):
        target = match.group(1).split("#", 1)[0].strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        if target and not target.startswith(("http://", "https://", "mailto:")):
            found.add(target.removeprefix("./"))
    for match in BACKTICK_PATH.finditer(text):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if "/" in target or re.search(r"\.[A-Za-z0-9]+$", target):
            found.add(target.split("#", 1)[0].removeprefix("./"))
    return found


def check_skill_package(root: Path, skill_dir: Path) -> list[str]:
    problems: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    files = [path for path in skill_dir.rglob("*") if path.is_file() or path.is_symlink()]
    for path in files:
        if path.is_symlink():
            problems.append(f"{display_path(root, path)} is a symlink")
    text = read_text(skill_md) if skill_md.is_file() else None
    referenced = extract_refs(text) if text is not None else set()
    for path in files:
        if path.is_symlink():
            continue
        relative = path.relative_to(skill_dir).as_posix()
        file_text = read_text(path)
        if file_text is None:
            problems.append(f"{display_path(root, path)} must be UTF-8 text")
            continue
        if "../" in file_text or "..\\" in file_text:
            problems.append(
                f"{display_path(root, path)} references a parent directory. "
                "Keep skill files inside the skill folder."
            )
        if path == skill_md:
            continue
        if relative not in referenced:
            problems.append(
                f"{display_path(root, path)} is not linked from SKILL.md. "
                "Add a relative link so an agent can find the file."
            )
    return problems


def check_skills(root: Path, catalog: dict) -> list[str]:
    problems: list[str] = []
    for entry in catalog["skills"]:
        skill_dir = root / entry["path"]
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        text = read_text(skill_md)
        if text is None:
            problems.append(f"{entry['path']}/SKILL.md must be UTF-8 text")
            continue
        meta, body, meta_problems = parse_frontmatter(text, f"{entry['path']}/SKILL.md")
        problems.extend(meta_problems)
        if meta is not None:
            if "name" not in meta or "description" not in meta:
                problems.append(f"{entry['path']}/SKILL.md frontmatter needs name and description")
            if meta.get("name") != entry["id"]:
                problems.append(f"{entry['path']}/SKILL.md name must be {entry['id']}")
            description = meta.get("description", "")
            if (
                not description
                or description != description.strip()
                or len(description) > MAX_SKILL_DESCRIPTION
            ):
                problems.append(
                    f"{entry['path']}/SKILL.md description must be one line "
                    f"of 1 to {MAX_SKILL_DESCRIPTION} characters"
                )
            if not body.strip():
                problems.append(f"{entry['path']}/SKILL.md is missing instructions")
            if entry["example"] and EXAMPLE_TOKEN.search(body) is None:
                problems.append(f"{entry['path']}/SKILL.md must contain the token EXAMPLE")
            if not entry["example"] and EXAMPLE_TOKEN.search(body):
                problems.append(
                    f"{entry['path']}/SKILL.md contains EXAMPLE. "
                    "Set example to true, or remove that token."
                )
        problems.extend(check_skill_package(root, skill_dir))
    return problems


def platform_lines(text: str) -> list[int]:
    return [number for number, line in enumerate(text.splitlines(), start=1) if PLATFORM_TERMS.search(line)]


def check_templates(root: Path, catalog: dict) -> list[str]:
    problems: list[str] = []
    for entry in catalog["templates"]:
        template_dir = root / entry["path"]
        if not template_dir.is_dir():
            continue
        for relative in TEMPLATE_FILES:
            if not (template_dir / relative).is_file():
                problems.append(f"{entry['path']}/{relative} is missing")
        meta_path = template_dir / "template.json"
        if meta_path.is_file():
            raw = read_text(meta_path)
            meta: object | None
            if raw is None:
                problems.append(f"{entry['path']}/template.json must be UTF-8 text")
                meta = None
            else:
                try:
                    meta = json.loads(raw)
                except json.JSONDecodeError as exc:
                    problems.append(f"{entry['path']}/template.json is not valid JSON ({exc})")
                    meta = None
            if isinstance(meta, dict):
                problems.extend(
                    check_exact_keys(meta, TEMPLATE_JSON_FIELDS, f"{entry['path']}/template.json")
                )
                for key in TEMPLATE_JSON_FIELDS:
                    if key in meta and meta[key] != entry[key]:
                        problems.append(
                            f"{entry['path']}/template.json {key} does not match catalog.json"
                        )
            elif meta is not None:
                problems.append(f"{entry['path']}/template.json must be an object")
        readme = template_dir / "README.md"
        readme_text = read_text(readme) if readme.is_file() else None
        if readme.is_file() and readme_text is None:
            problems.append(f"{entry['path']}/README.md must be UTF-8 text")
        if readme_text is not None:
            if entry["example"] and EXAMPLE_TOKEN.search(readme_text) is None:
                problems.append(f"{entry['path']}/README.md must contain the token EXAMPLE")
            if not entry["example"] and EXAMPLE_TOKEN.search(readme_text):
                problems.append(
                    f"{entry['path']}/README.md contains EXAMPLE. "
                    "Set example to true, or remove that token."
                )
            for token in README_MUST_MENTION:
                if token not in readme_text:
                    problems.append(f"{entry['path']}/README.md must mention {token}")
        for relative in CORE_FILES:
            path = template_dir / relative
            if not path.is_file():
                continue
            text = read_text(path)
            if text is None:
                problems.append(f"{entry['path']}/{relative} must be UTF-8 text")
                continue
            lines = platform_lines(text)
            if lines:
                joined = ", ".join(str(number) for number in lines)
                problems.append(
                    f"{entry['path']}/{relative} names a host product on line {joined}. "
                    "Put host setup in grok-bot.md and other-platforms.md."
                )
    return problems


def describe_tree_diff(left: Path, right: Path) -> str | None:
    if not right.exists():
        return "the copy is missing"
    if not right.is_dir():
        return "the copy is not a directory"
    left_names = {path.name for path in left.iterdir()}
    right_names = {path.name for path in right.iterdir()}
    parts: list[str] = []
    missing = sorted(left_names - right_names)
    extra = sorted(right_names - left_names)
    if missing:
        parts.append("missing in copy: " + ", ".join(missing))
    if extra:
        parts.append("extra in copy: " + ", ".join(extra))
    for name in sorted(left_names & right_names):
        left_path = left / name
        right_path = right / name
        if left_path.is_symlink() or right_path.is_symlink():
            parts.append(f"symlink: {name}")
        elif left_path.is_dir() and right_path.is_dir():
            nested = describe_tree_diff(left_path, right_path)
            if nested:
                parts.append(f"{name}/ ({nested})")
        elif left_path.is_file() and right_path.is_file():
            if not filecmp.cmp(left_path, right_path, shallow=False):
                parts.append(f"different file: {name}")
        else:
            parts.append(f"type mismatch: {name}")
    if not parts:
        return None
    return "; ".join(parts)


def remove_tree(path: Path) -> None:
    if path.is_symlink():
        raise RuntimeError(f"refusing to remove symlink {path}")
    shutil.rmtree(path)


def sync_copies(root: Path, catalog: dict, *, write: bool) -> tuple[list[str], list[str]]:
    problems: list[str] = []
    actions: list[str] = []
    for template in catalog["templates"]:
        rel_template = template["path"]
        try:
            skills_root = safe_join(root, Path(rel_template) / "skills")
        except RuntimeError as exc:
            problems.append(str(exc))
            continue
        expected = list(template["skills"])
        if skills_root.exists() and not skills_root.is_dir():
            problems.append(f"{rel_template}/skills is not a directory")
            continue
        actual = []
        if skills_root.is_dir():
            actual = sorted(path.name for path in skills_root.iterdir() if path.is_dir() or path.is_symlink())
        for name in actual:
            if name in expected:
                continue
            message = (
                f"{rel_template}/skills/{name} is not listed on the template. "
                "Run python3 scripts/sync_skills.py."
            )
            if write:
                try:
                    destination = safe_join(root, Path(rel_template) / "skills" / name)
                    remove_tree(destination)
                except RuntimeError as exc:
                    problems.append(str(exc))
                    continue
                actions.append(f"removed {rel_template}/skills/{name}")
            else:
                problems.append(message)
        for skill_id in expected:
            try:
                source = safe_join(root, Path("skills") / skill_id)
                destination = safe_join(root, Path(rel_template) / "skills" / skill_id)
            except RuntimeError as exc:
                problems.append(str(exc))
                continue
            if not source.is_dir():
                problems.append(f"{rel_template} lists {skill_id}, and skills/{skill_id} is missing")
                continue
            if destination.is_symlink():
                problems.append(f"{rel_template}/skills/{skill_id} is a symlink")
                continue
            diff = describe_tree_diff(source, destination)
            if diff is None:
                continue
            if not write:
                problems.append(
                    f"{rel_template}/skills/{skill_id} does not match skills/{skill_id} ({diff}). "
                    f"Edit skills/{skill_id} and run python3 scripts/sync_skills.py."
                )
                continue
            if destination.exists():
                remove_tree(destination)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, destination)
            actions.append(f"copied skills/{skill_id} -> {rel_template}/skills/{skill_id}")
    return problems, actions


def validate_repository(root: Path) -> list[str]:
    problems = check_schema_file(root)
    catalog, load_problems = read_catalog(root)
    problems.extend(load_problems)
    if catalog is None:
        return problems
    shape = check_catalog_shape(catalog)
    problems.extend(shape)
    if shape:
        return problems
    problems.extend(check_tree(root, catalog))
    problems.extend(check_skills(root, catalog))
    problems.extend(check_templates(root, catalog))
    drift, _actions = sync_copies(root, catalog, write=False)
    problems.extend(drift)
    return problems


def sync_repository(root: Path, *, write: bool) -> tuple[list[str], list[str]]:
    catalog, problems = read_catalog(root)
    if catalog is None:
        return problems, []
    shape = check_catalog_shape(catalog)
    problems.extend(shape)
    if shape:
        return problems, []
    drift, actions = sync_copies(root, catalog, write=write)
    if write:
        return problems, actions
    return drift, actions
