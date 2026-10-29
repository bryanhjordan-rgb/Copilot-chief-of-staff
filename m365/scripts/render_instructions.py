#!/usr/bin/env python3
"""Fill agent/instructions.md placeholders from a profile and check the length.

Usage:
  python3 m365/scripts/render_instructions.py [profile.yaml] [--out dist/instructions.md]

Default profile: m365/agent/profile.yaml (copy profile.example.yaml; it's gitignored).
Fails if any {{PLACEHOLDER}} is left or the result exceeds the instruction limit.
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

M365_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = M365_DIR / "agent" / "instructions.md"
DEFAULT_PROFILE = M365_DIR / "agent" / "profile.yaml"
DEFAULT_OUT = M365_DIR.parent / "dist" / "instructions.md"
MAX_CHARS = 8000

# placeholder -> profile key (all required)
SCALARS = {
    "YOUR_NAME": "name",
    "YOUR_FIRST_NAME": "first_name",
    "YOUR_ROLE": "role",
    "YOUR_COMPANY": "company",
    "DINNER_TIME": "home_by",
    "EARLIEST_MEETING_TIME": "earliest_meeting",
    "YOUR_TONE_DESCRIPTION": "tone",
}
CONSTRAINTS_LINE = "- {{ADD_YOUR_CONSTRAINTS}}\n"
PLACEHOLDER = re.compile(r"\{\{[A-Z_]+\}\}")


class ProfileError(Exception):
    pass


def render(template, profile):
    missing = [key for key in SCALARS.values() if not str(profile.get(key) or "").strip()]
    if missing:
        raise ProfileError(f"profile is missing: {', '.join(missing)}")

    lines = [f"- {c}" for c in profile.get("constraints") or []]
    if profile.get("key_people"):
        lines.append(
            "- Key people (always Tier 1 in triage, full stakeholder weight): "
            + "; ".join(profile["key_people"])
        )
    text = template.replace(CONSTRAINTS_LINE, "".join(f"{line}\n" for line in lines))
    for placeholder, key in SCALARS.items():
        text = text.replace("{{" + placeholder + "}}", str(profile[key]).strip())

    left = sorted(set(PLACEHOLDER.findall(text)))
    if left:
        raise ProfileError(f"unfilled placeholders: {', '.join(left)}")
    if len(text) > MAX_CHARS:
        raise ProfileError(f"rendered instructions are {len(text)} chars (max {MAX_CHARS}); shorten tone/constraints")
    return text


def main():
    parser = argparse.ArgumentParser(description="Render agent instructions from a profile.")
    parser.add_argument("profile", nargs="?", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    if not args.profile.is_file():
        sys.exit(f"{args.profile} not found; copy m365/agent/profile.example.yaml to it and fill it in")

    profile = yaml.safe_load(args.profile.read_text(encoding="utf-8")) or {}
    try:
        text = render(TEMPLATE.read_text(encoding="utf-8"), profile)
    except ProfileError as e:
        sys.exit(f"FAIL {e}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out} ({len(text)}/{MAX_CHARS} chars)")


if __name__ == "__main__":
    main()
