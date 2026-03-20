#!/usr/bin/env python3
"""SessionStart hook: migrate stale plugin permission rules.

When the Dev10x plugin updates, permission rules saved in
~/.claude/settings.json still reference the old version's cache
path (e.g. 0.4.0). This hook rewrites them to the current version.

Only runs when installed via plugin cache (not --plugin-dir).
"""

import json
import sys
from pathlib import Path


def get_plugin_root() -> Path:
    script = Path(__file__).resolve()
    return script.parent.parent.parent


def is_cache_install(plugin_root: Path) -> bool:
    return "plugins/cache/" in str(plugin_root)


def find_settings_files() -> list[Path]:
    home = Path.home()
    candidates = [
        home / ".claude" / "settings.json",
        home / ".claude" / "settings.local.json",
    ]
    return [f for f in candidates if f.exists()]


def build_old_prefixes(
    plugin_root: Path,
    home: str,
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Build (old_path, new_path) pairs for absolute and tilde forms."""
    version_parent = plugin_root.parent
    current_abs = str(plugin_root) + "/"
    current_tilde = current_abs.replace(home, "~")

    pairs_abs: list[tuple[str, str]] = []
    pairs_tilde: list[tuple[str, str]] = []

    try:
        children = sorted(version_parent.iterdir())
    except OSError:
        return pairs_abs, pairs_tilde

    for child in children:
        if not child.is_dir() or child == plugin_root:
            continue
        old_abs = str(child) + "/"
        old_tilde = old_abs.replace(home, "~")
        pairs_abs.append((old_abs, current_abs))
        pairs_tilde.append((old_tilde, current_tilde))

    return pairs_abs, pairs_tilde


def migrate_rules(
    rules: list[str],
    replacements: list[tuple[str, str]],
) -> tuple[list[str], int]:
    migrated = 0
    result = []
    for rule in rules:
        new_rule = rule
        for old, new in replacements:
            if old in rule:
                new_rule = rule.replace(old, new)
                migrated += 1
                break
        result.append(new_rule)
    return result, migrated


def deduplicate_rules(rules: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for rule in rules:
        if rule not in seen:
            seen.add(rule)
            deduped.append(rule)
    return deduped


def process_settings(
    settings: dict,
    all_replacements: list[tuple[str, str]],
) -> tuple[dict, int]:
    total = 0
    permissions = settings.get("permissions", {})

    for key in ("allow", "deny"):
        rules = permissions.get(key, [])
        if not rules:
            continue
        rules, count = migrate_rules(rules, all_replacements)
        rules = deduplicate_rules(rules)
        total += count
        permissions[key] = rules

    return settings, total


def main() -> None:
    plugin_root = get_plugin_root()

    if not is_cache_install(plugin_root):
        sys.exit(0)

    home = str(Path.home())
    pairs_abs, pairs_tilde = build_old_prefixes(plugin_root, home)

    if not pairs_abs and not pairs_tilde:
        sys.exit(0)

    all_replacements = pairs_abs + pairs_tilde

    total_migrated = 0
    files_changed: list[str] = []

    for settings_file in find_settings_files():
        try:
            text = settings_file.read_text()
            settings = json.loads(text)
        except (json.JSONDecodeError, OSError):
            continue

        settings, count = process_settings(settings, all_replacements)

        if count > 0:
            try:
                settings_file.write_text(json.dumps(settings, indent=2) + "\n")
            except OSError:
                continue
            total_migrated += count
            files_changed.append(settings_file.name)

    if total_migrated > 0:
        files_str = ", ".join(files_changed)
        print(
            f"Migrated {total_migrated} stale permission rule(s) "
            f"to current plugin version in {files_str}"
        )


if __name__ == "__main__":
    main()
