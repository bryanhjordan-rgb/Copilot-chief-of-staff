#!/usr/bin/env python3
"""Build the deployment kit: everything Copilot Studio and Power Automate need, in one folder.

Usage:
  python3 m365/scripts/release.py [--profile m365/agent/profile.yaml] [--goals goals.yaml]

Output: dist/kit/ and dist/ChiefOfStaff-kit.zip containing
  ChiefOfStaff.xlsx           workbook (with your goals if --goals)
  instructions.md             rendered from the profile, or the raw template if none
  skills/<name>.zip           one per skill, ready for Copilot Studio > Skills > Upload
  cards/*.card.json           Adaptive Cards for the flows
  office-scripts/*.ts         paste into Excel > Automate
  CHECKLIST.md                deployment order with what's in this kit
Fails before writing anything if skills don't validate or the profile doesn't render.
"""

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import build_workbook  # noqa: E402
import render_instructions  # noqa: E402
import skills  # noqa: E402
import yaml  # noqa: E402

M365_DIR = SCRIPTS.parent
DIST = M365_DIR.parent / "dist"
KIT = DIST / "kit"
KIT_ZIP = DIST / "ChiefOfStaff-kit.zip"


def git_commit():
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=M365_DIR, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def instructions(profile_path):
    template = skills.INSTRUCTIONS.read_text(encoding="utf-8")
    if not profile_path:
        return template, False
    profile = yaml.safe_load(Path(profile_path).read_text(encoding="utf-8")) or {}
    return render_instructions.render(template, profile), True


def skill_versions():
    versions = {}
    for skill_dir in skills.skill_dirs():
        meta, _ = skills.parse_skill(skill_dir / "SKILL.md")
        versions[skill_dir.name] = meta["metadata"]["version"]
    return versions


def checklist(rendered, goals, versions):
    skill_rows = "\n".join(f"| `{name}` | {version} |" for name, version in versions.items())
    return f"""# Chief of Staff — deployment kit

Commit `{git_commit()}` · instructions {"rendered from your profile" if rendered else "**NOT rendered**: still has {{PLACEHOLDERS}} (run with --profile)"} · workbook {"includes your goals" if goals else "has an empty Goals sheet"}

Full walkthrough: `m365/docs/08-build-guide.md`. Use this list to tick off a deploy.

## Phase 1 (conversational)
- [ ] Upload `ChiefOfStaff.xlsx` to OneDrive › Apps › ChiefOfStaff
- [ ] Create the agent; paste `instructions.md` into Instructions
- [ ] Add the 4 Excel Online (Business) tools (list/get/add/update rows) pointed at the workbook
- [ ] Add Work IQ (or the Outlook/Teams connectors)
- [ ] Skills › Upload: `skills/prioritize.zip`, `skills/intake.zip`, `skills/daily-brief.zip`
- [ ] Run the smoke test in the build guide, step 6
- [ ] Publish to Microsoft 365 Copilot + Teams

## Phase 2 (automation)
- [ ] Skills › Upload: `reconcile`, `triage`, `meeting-prep`, `meeting-debrief`
- [ ] Flow: daily brief (`m365/flows/daily-brief.md`) with `cards/daily-brief.card.json`
- [ ] Flow: completion detector with `cards/completion-confirm.card.json`

## Phase 3 (learning loop)
- [ ] Excel › Automate › New Script: paste `office-scripts/mine-signatures.ts`, save as `mine-signatures`
- [ ] Skills › Upload: `skills/skill-miner.zip`
- [ ] Flow: weekly skill review with `cards/weekly-review.card.json`

## Skills in this kit

| Skill | Version |
|-------|---------|
{skill_rows}
"""


def build_kit(profile_path=None, goals_path=None):
    if not skills.validate():
        sys.exit("FAIL skills did not validate; nothing written")
    try:
        text, rendered = instructions(profile_path)
    except render_instructions.ProfileError as e:
        sys.exit(f"FAIL {e}; nothing written")

    if KIT.exists():
        shutil.rmtree(KIT)
    (KIT / "skills").mkdir(parents=True)
    build_workbook.build(KIT / "ChiefOfStaff.xlsx", goals_path)
    (KIT / "instructions.md").write_text(text, encoding="utf-8")
    skills.package()
    for archive in sorted(skills.DIST_DIR.glob("*.zip")):
        shutil.copy2(archive, KIT / "skills" / archive.name)
    shutil.copytree(M365_DIR / "flows" / "cards", KIT / "cards", ignore=shutil.ignore_patterns("*.md"))
    (KIT / "office-scripts").mkdir()
    for script in sorted((M365_DIR / "office-scripts").glob("*.ts")):
        if not script.name.endswith(".d.ts"):  # type stubs are for local tsc only
            shutil.copy2(script, KIT / "office-scripts" / script.name)
    (KIT / "CHECKLIST.md").write_text(checklist(rendered, bool(goals_path), skill_versions()), encoding="utf-8")

    with zipfile.ZipFile(KIT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(KIT.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(KIT))
    print(f"wrote {KIT_ZIP} ({'rendered' if rendered else 'UNRENDERED'} instructions)")
    return KIT


def main():
    parser = argparse.ArgumentParser(description="Build the Chief of Staff deployment kit.")
    parser.add_argument("--profile", type=Path, help="profile.yaml to render instructions (default: agent/profile.yaml if present)")
    parser.add_argument("--goals", type=Path, help="goals.yaml to load into the workbook")
    args = parser.parse_args()
    profile = args.profile or (render_instructions.DEFAULT_PROFILE if render_instructions.DEFAULT_PROFILE.is_file() else None)
    build_kit(profile, args.goals)


if __name__ == "__main__":
    main()
