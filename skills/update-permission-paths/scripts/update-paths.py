#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Update versioned Dev10x plugin paths in .claude/settings.local.json files.

Scans project roots defined in a user config file, finds all settings files
with versioned plugin cache paths, and replaces old versions with the latest
installed version.

Config lookup order:
  1. ~/.claude/skills/dev10x:update-permission-paths/projects.yaml (userspace)
  2. ${CLAUDE_PLUGIN_ROOT}/skills/update-permission-paths/projects.yaml (plugin default)
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

USERSPACE_CONFIG = (
    Path.home() / ".claude" / "skills" / "dev10x:update-permission-paths" / "projects.yaml"
)
PLUGIN_CONFIG = Path(__file__).resolve().parent.parent / "projects.yaml"
VERSION_PATTERN = re.compile(r"(plugins/cache/WooYek/Dev10x/)(\d+\.\d+\.\d+)")


def find_config() -> Path:
    if USERSPACE_CONFIG.is_file():
        return USERSPACE_CONFIG
    if PLUGIN_CONFIG.is_file():
        return PLUGIN_CONFIG
    print(
        f"ERROR: No config found. Create {USERSPACE_CONFIG}\nor ensure {PLUGIN_CONFIG} exists.",
        file=sys.stderr,
    )
    sys.exit(1)


def load_config(config_path: Path) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def detect_latest_version(cache_dir: Path) -> str | None:
    if not cache_dir.is_dir():
        return None
    versions = sorted(
        cache_dir.iterdir(),
        key=lambda p: _version_tuple(p.name),
    )
    return versions[-1].name if versions else None


def _version_tuple(version: str) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in version.split("."))
    except ValueError:
        return (0,)


def find_settings_files(
    roots: list[str],
    *,
    include_user: bool,
) -> list[Path]:
    files: list[Path] = []
    if include_user:
        user_settings = Path.home() / ".claude" / "settings.local.json"
        if user_settings.exists():
            files.append(user_settings)

    project_settings_dir = Path.home() / ".claude" / "projects"
    if project_settings_dir.is_dir():
        for settings_file in project_settings_dir.rglob("settings.local.json"):
            files.append(settings_file)

    for root in roots:
        root_path = Path(root).expanduser()
        if not root_path.is_dir():
            continue
        for settings_file in root_path.rglob(".claude/settings.local.json"):
            files.append(settings_file)

    seen: set[Path] = set()
    unique: list[Path] = []
    for f in files:
        resolved = f.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def update_file(
    path: Path,
    target_version: str,
    *,
    dry_run: bool = False,
) -> tuple[int, list[str]]:
    content = path.read_text()
    old_versions: set[str] = set()
    count = 0

    def replacer(match: re.Match) -> str:
        nonlocal count
        old_ver = match.group(2)
        if old_ver != target_version:
            old_versions.add(old_ver)
            count += 1
            return match.group(1) + target_version
        return match.group(0)

    new_content = VERSION_PATTERN.sub(replacer, content)

    if count > 0 and not dry_run:
        try:
            json.loads(new_content)
        except json.JSONDecodeError as e:
            return 0, [f"  SKIP (invalid JSON after replacement): {e}"]

        path.write_text(new_content)

    messages = []
    for old_ver in sorted(old_versions):
        messages.append(f"  {old_ver} -> {target_version} ({count} replacements)")
    return count, messages


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update Dev10x plugin version paths in settings files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )
    parser.add_argument(
        "--version",
        help="Target version (default: auto-detect latest installed)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Create userspace config from plugin default",
    )
    args = parser.parse_args()

    if args.init:
        return _init_userspace_config()

    config_path = find_config()
    print(f"Config: {config_path}")
    config = load_config(config_path)

    cache_dir = Path(config["plugin_cache"]).expanduser()
    target = args.version or detect_latest_version(cache_dir)

    if not target:
        print(f"ERROR: No versions found in {cache_dir}", file=sys.stderr)
        return 1

    print(f"Target version: {target}")
    if args.dry_run:
        print("(dry run — no files will be modified)\n")

    settings_files = find_settings_files(
        roots=config.get("roots", []),
        include_user=config.get("include_user_settings", True),
    )

    if not settings_files:
        print("No settings files found.")
        return 0

    total_changes = 0
    files_changed = 0

    for path in sorted(settings_files):
        count, messages = update_file(path, target, dry_run=args.dry_run)
        if count > 0:
            print(f"\n{path}")
            for msg in messages:
                print(msg)
            total_changes += count
            files_changed += 1

    if total_changes == 0:
        print("\nAll files already up to date.")
    else:
        verb = "Would update" if args.dry_run else "Updated"
        print(f"\n{verb} {total_changes} paths in {files_changed} files.")

    return 0


def _init_userspace_config() -> int:
    if USERSPACE_CONFIG.is_file():
        print(f"Config already exists: {USERSPACE_CONFIG}")
        return 0
    if not PLUGIN_CONFIG.is_file():
        print(f"ERROR: Plugin default config not found: {PLUGIN_CONFIG}", file=sys.stderr)
        return 1
    USERSPACE_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    USERSPACE_CONFIG.write_text(PLUGIN_CONFIG.read_text())
    print(f"Created: {USERSPACE_CONFIG}")
    print("Edit this file to add your project roots.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
