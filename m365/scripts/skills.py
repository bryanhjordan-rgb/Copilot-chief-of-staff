#!/usr/bin/env python3
"""Validate and package Chief of Staff skills for Copilot Studio.

Usage:
  python3 m365/scripts/skills.py validate            # all skills + instructions
  python3 m365/scripts/skills.py package             # validate, then zip to dist/skills/
  python3 m365/scripts/skills.py check-instructions  # instructions length only
  python3 m365/scripts/skills.py export-evals        # evals -> dist/evals.csv (one row per case)

Skills follow the open Agent Skills format (SKILL.md with YAML frontmatter).
Repo-specific fields live under `metadata` so the files stay portable.
"""

import csv
import re
import sys
import zipfile
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

M365_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = M365_DIR / "skills"
INSTRUCTIONS = M365_DIR / "agent" / "instructions.md"
DIST_DIR = M365_DIR.parent / "dist" / "skills"
EVALS_DIR = M365_DIR / "evals"
EVALS_CSV = M365_DIR.parent / "dist" / "evals.csv"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SIGNATURE_RE = re.compile(r"^[a-z0-9-]+\|[a-z0-9-]+\|[a-z0-9-]+$")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_INSTRUCTIONS = 8000
REQUIRED_METADATA = ("version", "signatures", "tools")
REQUIRED_SECTIONS = ("## Goal", "## Steps", "## Guardrails", "## Done when")
TEMPLATE_DIR = "_template"
MIN_EVAL_CASES = 3
EVAL_CASE_KEYS = {"id", "say", "given", "expect", "workbook", "must_not"}


def parse_skill(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        return None, text
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def validate_skill(skill_dir):
    errors = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return [f"{skill_dir.name}: missing SKILL.md"]

    meta, body = parse_skill(skill_file)
    if meta is None:
        return [f"{skill_dir.name}: SKILL.md has no YAML frontmatter"]

    name = meta.get("name", "")
    if not NAME_RE.match(str(name)) or len(name) > MAX_NAME:
        errors.append(f"name '{name}' must be kebab-case, <= {MAX_NAME} chars")
    if name != skill_dir.name:
        errors.append(f"name '{name}' must match directory '{skill_dir.name}'")

    description = str(meta.get("description", "")).strip()
    if not description:
        errors.append("description is required")
    elif len(description) > MAX_DESCRIPTION:
        errors.append(f"description is {len(description)} chars (max {MAX_DESCRIPTION})")

    metadata = meta.get("metadata") or {}
    if not isinstance(metadata, dict):
        errors.append("metadata must be a mapping")
        metadata = {}
    for key in REQUIRED_METADATA:
        if key not in metadata:
            errors.append(f"metadata.{key} is required")
    for key, value in metadata.items():
        if not isinstance(value, str):
            errors.append(f"metadata.{key} must be a quoted string")
    for signature in str(metadata.get("signatures", "")).split(","):
        if signature.strip() and not SIGNATURE_RE.match(signature.strip()):
            errors.append(f"signature '{signature.strip()}' must be verb|object|counterpart")

    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"missing section '{section}'")

    return [f"{skill_dir.name}: {e}" for e in errors]


def load_evals(name):
    path = EVALS_DIR / f"{name}.yaml"
    if not path.is_file():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def validate_evals(name):
    evals = load_evals(name)
    if evals is None:
        return [f"{name}: missing evals/{name}.yaml"]
    errors = []
    if evals.get("skill") != name:
        errors.append(f"evals skill '{evals.get('skill')}' must be '{name}'")
    cases = evals.get("cases") or []
    if len(cases) < MIN_EVAL_CASES:
        errors.append(f"evals need >= {MIN_EVAL_CASES} cases (found {len(cases)})")
    seen = set()
    for case in cases:
        case_id = case.get("id", "")
        if not str(case_id).startswith(f"{name}-"):
            errors.append(f"eval id '{case_id}' must start with '{name}-'")
        if case_id in seen:
            errors.append(f"eval id '{case_id}' is duplicated")
        seen.add(case_id)
        unknown = set(case) - EVAL_CASE_KEYS
        if unknown:
            errors.append(f"eval '{case_id}' has unknown keys: {sorted(unknown)}")
        if not isinstance(case.get("say"), str) or not case["say"].strip():
            errors.append(f"eval '{case_id}' needs a 'say' string")
        if not (case.get("expect") or case.get("workbook")):
            errors.append(f"eval '{case_id}' needs 'expect' or 'workbook' checks")
        for key in ("expect", "workbook", "must_not"):
            value = case.get(key, [])
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                errors.append(f"eval '{case_id}' {key} must be a list of strings")
    return [f"{name}: {e}" for e in errors]


def skill_dirs():
    return sorted(
        d for d in SKILLS_DIR.iterdir()
        if d.is_dir() and d.name != TEMPLATE_DIR
    )


def check_instructions():
    length = len(INSTRUCTIONS.read_text(encoding="utf-8"))
    if length > MAX_INSTRUCTIONS:
        return [f"instructions.md is {length} chars (max {MAX_INSTRUCTIONS})"]
    print(f"instructions.md: {length}/{MAX_INSTRUCTIONS} chars")
    return []


def validate():
    errors = check_instructions()
    for skill_dir in skill_dirs():
        skill_errors = validate_skill(skill_dir) + validate_evals(skill_dir.name)
        errors.extend(skill_errors)
        if not skill_errors:
            print(f"ok   {skill_dir.name}")
    for error in errors:
        print(f"FAIL {error}")
    return not errors


def package():
    if not validate():
        return False
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    for skill_dir in skill_dirs():
        target = DIST_DIR / f"{skill_dir.name}.zip"
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in sorted(skill_dir.rglob("*")):
                if file.is_file():
                    zf.write(file, file.relative_to(skill_dir))
        print(f"packaged {target.relative_to(M365_DIR.parent)}")
    return True


def export_evals():
    if not validate():
        return False
    EVALS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with EVALS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["skill", "id", "given", "say", "expected", "must_not"])
        for skill_dir in skill_dirs():
            for case in load_evals(skill_dir.name)["cases"]:
                writer.writerow([
                    skill_dir.name,
                    case["id"],
                    case.get("given", ""),
                    case["say"],
                    "\n".join(case.get("expect", []) + case.get("workbook", [])),
                    "\n".join(case.get("must_not", [])),
                ])
    print(f"wrote {EVALS_CSV.relative_to(M365_DIR.parent)}")
    return True


def instructions_only():
    errors = check_instructions()
    for error in errors:
        print(f"FAIL {error}")
    return not errors


COMMANDS = {
    "validate": validate,
    "package": package,
    "check-instructions": instructions_only,
    "export-evals": export_evals,
}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        sys.exit(__doc__)
    sys.exit(0 if COMMANDS[sys.argv[1]]() else 1)
