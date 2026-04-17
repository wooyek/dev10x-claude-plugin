"""Maintain Dev10x plugin permission settings across all projects.

Modes:
  - (default) Update versioned plugin cache paths to the latest version
  - ensure-base: Add missing base permissions from projects.yaml
  - generalize: Replace session-specific args with wildcard patterns

Config lookup order:
  1. ~/.claude/memory/Dev10x/projects.yaml (persistent user config)
  2. ~/.claude/skills/Dev10x:upgrade-cleanup/projects.yaml (userspace)
  3. ${CLAUDE_PLUGIN_ROOT}/skills/upgrade-cleanup/projects.yaml (plugin default)

CLI entry point: ``dev10x permission update-paths`` (and siblings).
"""

import json
import re
import sys
from pathlib import Path

import yaml

MEMORY_CONFIG = Path.home() / ".claude" / "memory" / "Dev10x" / "projects.yaml"
USERSPACE_CONFIG = Path.home() / ".claude" / "skills" / "Dev10x:upgrade-cleanup" / "projects.yaml"
PLUGIN_CONFIG = (
    Path(__file__).resolve().parents[4] / "skills" / "upgrade-cleanup" / "projects.yaml"
)
PLUGIN_NAMES = r"(?:Dev10x|dev10x-claude)"
VERSION_PATTERN = re.compile(rf"(plugins/cache/)([^/]+)(/{PLUGIN_NAMES}/)(\d+\.\d+\.\d+)")


def extract_cache_publisher(plugin_cache: str) -> str | None:
    path = Path(plugin_cache).expanduser()
    parts = list(path.parts)
    for i, part in enumerate(parts):
        if part == "cache" and i >= 2 and parts[i - 1] == "plugins":
            if i + 1 < len(parts):
                return parts[i + 1]
    return None


def find_config() -> Path:
    if MEMORY_CONFIG.is_file():
        return MEMORY_CONFIG
    if USERSPACE_CONFIG.is_file():
        return USERSPACE_CONFIG
    if PLUGIN_CONFIG.is_file():
        return PLUGIN_CONFIG
    print(
        f"ERROR: No config found. Create {MEMORY_CONFIG}\nor ensure {PLUGIN_CONFIG} exists.",
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
    target_publisher: str | None = None,
    dry_run: bool = False,
) -> tuple[int, list[str]]:
    content = path.read_text()
    old_versions: set[str] = set()
    old_publishers: set[str] = set()
    count = 0

    def replacer(match: re.Match) -> str:
        nonlocal count
        prefix = match.group(1)
        publisher = match.group(2)
        plugin_slug = match.group(3)
        old_ver = match.group(4)

        new_publisher = publisher
        new_ver = old_ver
        changed = False

        if target_publisher and publisher != target_publisher:
            old_publishers.add(publisher)
            new_publisher = target_publisher
            changed = True

        if old_ver != target_version:
            old_versions.add(old_ver)
            new_ver = target_version
            changed = True

        if changed:
            count += 1
            return prefix + new_publisher + plugin_slug + new_ver
        return match.group(0)

    new_content = VERSION_PATTERN.sub(replacer, content)

    if count > 0 and not dry_run:
        try:
            json.loads(new_content)
        except json.JSONDecodeError as e:
            return 0, [f"  SKIP (invalid JSON after replacement): {e}"]

        from dev10x.skills.permission.backup import create_backup

        create_backup(path)
        path.write_text(new_content)

    messages = []
    for old_pub in sorted(old_publishers):
        messages.append(f"  publisher: {old_pub} -> {target_publisher}")
    for old_ver in sorted(old_versions):
        messages.append(f"  {old_ver} -> {target_version} ({count} replacements)")
    return count, messages


def ensure_base_permissions(
    path: Path,
    base_permissions: list[str],
    *,
    dry_run: bool = False,
) -> tuple[int, list[str]]:
    content = path.read_text()
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return 0, [f"  SKIP (invalid JSON): {e}"]

    allow_list: list[str] = data.get("permissions", {}).get("allow", [])
    existing = {r for r in allow_list if not _is_nonfunctional_mcp_wildcard(r)}
    stale_wildcards = [r for r in allow_list if _is_nonfunctional_mcp_wildcard(r)]
    missing = [p for p in base_permissions if p not in existing]

    if not missing and not stale_wildcards:
        return 0, []

    if not dry_run:
        from dev10x.skills.permission.backup import create_backup
        from dev10x.skills.permission.file_lock import locked_json_update

        create_backup(path)
        with locked_json_update(path=path) as live_data:
            if "permissions" not in live_data:
                live_data["permissions"] = {}
            if "allow" not in live_data["permissions"]:
                live_data["permissions"]["allow"] = []
            if stale_wildcards:
                live_data["permissions"]["allow"] = [
                    r
                    for r in live_data["permissions"]["allow"]
                    if not _is_nonfunctional_mcp_wildcard(r)
                ]
            live_data["permissions"]["allow"].extend(missing)

    messages = [f"  - {wc}  (non-functional MCP wildcard removed)" for wc in stale_wildcards]
    messages.extend(f"  + {p}" for p in missing)
    return len(missing) + len(stale_wildcards), messages


SCRIPT_SCAN_GLOBS: list[str] = [
    "bin/*.sh",
    "hooks/scripts/*.py",
    "hooks/scripts/*.sh",
    "skills/*/scripts/*.py",
    "skills/*/scripts/*.sh",
]


def scan_plugin_scripts(plugin_root: Path) -> list[Path]:
    scripts: list[Path] = []
    for glob_pattern in SCRIPT_SCAN_GLOBS:
        scripts.extend(plugin_root.glob(glob_pattern))
    return sorted(set(scripts))


def build_script_allow_rules(
    scripts: list[Path],
    *,
    plugin_root: Path,
) -> list[str]:
    rules: list[str] = []
    for script in scripts:
        relative = script.relative_to(plugin_root)
        rule = f"Bash({plugin_root}/{relative}:*)"
        rules.append(rule)
    return rules


def verify_script_coverage(
    settings_path: Path,
    expected_rules: list[str],
) -> tuple[list[str], list[str]]:
    content = settings_path.read_text()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return [], expected_rules

    allow_list: list[str] = data.get("permissions", {}).get("allow", [])

    covered: list[str] = []
    missing: list[str] = []
    for rule in expected_rules:
        match = re.search(r"Bash\((.+?):\*\)", rule)
        if not match:
            missing.append(rule)
            continue
        script_name = Path(match.group(1)).name
        pattern = re.compile(rf"Bash\(.*/{re.escape(script_name)}:\*\)")
        if rule in allow_list or any(pattern.search(entry) for entry in allow_list):
            covered.append(rule)
        else:
            missing.append(rule)
    return covered, missing


def ensure_script_rules(
    settings_path: Path,
    missing_rules: list[str],
    *,
    dry_run: bool = False,
) -> tuple[int, list[str]]:
    if not missing_rules:
        return 0, []

    if not dry_run:
        from dev10x.skills.permission.backup import create_backup
        from dev10x.skills.permission.file_lock import locked_json_update

        create_backup(settings_path)
        with locked_json_update(path=settings_path) as data:
            if "permissions" not in data:
                data["permissions"] = {}
            if "allow" not in data["permissions"]:
                data["permissions"]["allow"] = []
            data["permissions"]["allow"].extend(missing_rules)

    messages = [f"  + {rule}" for rule in missing_rules]
    return len(missing_rules), messages


GENERALIZE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(detect-tracker\.sh)\s+[^)]+"), r"\1:*"),
    (re.compile(r"(gh-issue-get\.sh)\s+[^)]+"), r"\1:*"),
    (re.compile(r"(gh-pr-detect\.sh)\s+[^)]+"), r"\1:*"),
    (re.compile(r"(generate-commit-list\.sh)\s+[^)]+"), r"\1:*"),
    (re.compile(r"(extract-session\.sh)\s+[^)]+"), r"\1:*"),
    (re.compile(r"(\.(?:sh|py))\s+[^):]+(?::\*)?"), r"\1:*"),
    (re.compile(r"(/tmp/Dev10x/[^/]+/)[^/)]+\.[A-Za-z0-9]{6,}\.(txt|md|json)"), r"\1*"),
    (re.compile(r"(git reset --hard) origin/\S+"), r"\1"),
    (re.compile(r"(git reset --soft) [A-Fa-f0-9]{6,}"), r"\1"),
]


def generalize_permission(entry: str) -> str | None:
    original = entry
    for pattern, replacement in GENERALIZE_PATTERNS:
        entry = pattern.sub(replacement, entry)
    if entry != original:
        return entry
    return None


def generalize_permissions(
    path: Path,
    *,
    dry_run: bool = False,
) -> tuple[int, list[str]]:
    content = path.read_text()
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return 0, [f"  SKIP (invalid JSON): {e}"]

    allow_list: list[str] = data.get("permissions", {}).get("allow", [])
    if not allow_list:
        return 0, []

    existing = set(allow_list)
    replacements: list[tuple[str, str]] = []
    for entry in allow_list:
        generalized = generalize_permission(entry)
        if generalized and generalized != entry and generalized not in existing:
            replacements.append((entry, generalized))

    if not replacements:
        return 0, []

    if not dry_run:
        from dev10x.skills.permission.backup import create_backup

        create_backup(path)
        new_allow = list(allow_list)
        for old, new in replacements:
            idx = new_allow.index(old)
            new_allow[idx] = new
        data["permissions"]["allow"] = new_allow
        path.write_text(json.dumps(data, indent=2) + "\n")

    messages = [f"  {old} → {new}" for old, new in replacements]
    return len(replacements), messages


def _restore(*, config_path: Path) -> int:
    from dev10x.skills.permission.backup import restore_all

    config = load_config(config_path)
    settings_files = find_settings_files(
        roots=config.get("roots", []),
        include_user=config.get("include_user_settings", True),
    )
    restored = restore_all(paths=settings_files)
    if not restored:
        print("No backups found to restore.")
        return 0
    for original, backup in restored:
        print(f"  Restored {original} from {backup.name}")
    print(f"\nRestored {len(restored)} files.")
    return 0


MCP_WILDCARD_PATTERN = re.compile(r"^mcp__plugin_[A-Za-z0-9]+_\*$")


def _is_nonfunctional_mcp_wildcard(rule: str) -> bool:
    return bool(MCP_WILDCARD_PATTERN.match(rule))


def _load_global_allow_rules() -> tuple[set[str], list[str]]:
    global_settings = Path.home() / ".claude" / "settings.json"
    if not global_settings.is_file():
        return set(), []
    try:
        data = json.loads(global_settings.read_text())
        all_rules = data.get("permissions", {}).get("allow", [])
        wildcards = [r for r in all_rules if _is_nonfunctional_mcp_wildcard(r)]
        effective = {r for r in all_rules if not _is_nonfunctional_mcp_wildcard(r)}
        return effective, wildcards
    except (json.JSONDecodeError, OSError):
        return set(), []


def _ensure_base(
    *,
    config: dict,
    settings_files: list[Path],
    dry_run: bool,
    quiet: bool = False,
) -> int:
    base_permissions = config.get("base_permissions", [])
    if not base_permissions:
        print("No base_permissions defined in config.")
        return 0

    global_rules, stale_wildcards = _load_global_allow_rules()
    filtered = [p for p in base_permissions if p not in global_rules]
    skipped = len(base_permissions) - len(filtered)

    if not quiet:
        print(f"Base permissions: {len(base_permissions)} rules")
        if stale_wildcards:
            print(
                f"  WARNING: {len(stale_wildcards)} non-functional MCP wildcard(s)"
                " in global settings.json:"
            )
            for wc in stale_wildcards:
                print(f"    - {wc}  (Claude Code ignores MCP wildcards)")
        if skipped > 0:
            print(f"  Skipping {skipped} already in global settings.json")
        if dry_run:
            print("(dry run — no files will be modified)\n")

    if not filtered:
        if not quiet:
            print("All base permissions already covered by global settings.")
        return 0

    total_added = 0
    files_changed = 0

    for path in sorted(settings_files):
        count, messages = ensure_base_permissions(
            path,
            filtered,
            dry_run=dry_run,
        )
        if count > 0:
            if not quiet:
                print(f"\n{path}")
                for msg in messages:
                    print(msg)
            total_added += count
            files_changed += 1

    if total_added == 0:
        print("All files already have base permissions.")
    else:
        verb = "Would add" if dry_run else "Added"
        print(f"{verb} {total_added} permissions across {files_changed} files.")

    return 0


def _generalize(
    *,
    settings_files: list[Path],
    dry_run: bool,
    quiet: bool = False,
) -> int:
    if dry_run and not quiet:
        print("(dry run — no files will be modified)\n")

    total_generalized = 0
    files_changed = 0

    for path in sorted(settings_files):
        count, messages = generalize_permissions(path, dry_run=dry_run)
        if count > 0:
            if not quiet:
                print(f"\n{path}")
                for msg in messages:
                    print(msg)
            total_generalized += count
            files_changed += 1

    if total_generalized == 0:
        print("No session-specific permissions found.")
    else:
        verb = "Would generalize" if dry_run else "Generalized"
        print(f"{verb} {total_generalized} permissions in {files_changed} files.")

    return 0


def _ensure_scripts(
    *,
    config: dict,
    settings_files: list[Path],
    dry_run: bool,
    quiet: bool = False,
) -> int:
    cache_dir = Path(config["plugin_cache"]).expanduser()
    target_version = detect_latest_version(cache_dir)
    if not target_version:
        print(f"ERROR: No versions found in {cache_dir}", file=sys.stderr)
        return 1

    plugin_root = cache_dir / target_version
    scripts = scan_plugin_scripts(plugin_root)
    if not scripts:
        print(f"No callable scripts found in {plugin_root}")
        return 0

    expected_rules = build_script_allow_rules(
        scripts,
        plugin_root=plugin_root,
    )

    if not quiet:
        print(f"Plugin root: {plugin_root}")
        print(f"Scripts found: {len(scripts)}")
        if dry_run:
            print("(dry run — no files will be modified)\n")

    total_added = 0
    files_changed = 0

    for path in sorted(settings_files):
        _covered, missing = verify_script_coverage(
            settings_path=path,
            expected_rules=expected_rules,
        )
        if not missing:
            continue

        count, messages = ensure_script_rules(
            settings_path=path,
            missing_rules=missing,
            dry_run=dry_run,
        )
        if count > 0:
            if not quiet:
                print(f"\n{path}")
                for msg in messages:
                    print(msg)
            total_added += count
            files_changed += 1

    if total_added == 0:
        print("All settings files have complete script coverage.")
    else:
        verb = "Would add" if dry_run else "Added"
        print(f"{verb} {total_added} script rules across {files_changed} files.")

    return 0


KNOWN_PLUGIN_DIRS = ("Dev10x", "dev10x-claude")


def _detect_plugin_cache() -> str:
    cache_root = Path.home() / ".claude" / "plugins" / "cache"
    if not cache_root.is_dir():
        return "~/.claude/plugins/cache/Dev10x-Guru/Dev10x"
    candidates: list[Path] = []
    for org_dir in cache_root.iterdir():
        if not org_dir.is_dir():
            continue
        for plugin_name in KNOWN_PLUGIN_DIRS:
            plugin_dir = org_dir / plugin_name
            if plugin_dir.is_dir():
                candidates.append(plugin_dir)
                break
    if len(candidates) == 1:
        return f"~/.claude/plugins/cache/{candidates[0].parent.name}/{candidates[0].name}"
    if len(candidates) > 1:
        names = ", ".join(f"{c.parent.name}/{c.name}" for c in candidates)
        print(f"Multiple plugin cache entries found: {names}")
        print(f"Using first match: {candidates[0].parent.name}/{candidates[0].name}")
        return f"~/.claude/plugins/cache/{candidates[0].parent.name}/{candidates[0].name}"
    return "~/.claude/plugins/cache/Dev10x-Guru/Dev10x"


def _init_userspace_config() -> int:
    if MEMORY_CONFIG.is_file():
        print(f"Config already exists: {MEMORY_CONFIG}")
        return 0
    if USERSPACE_CONFIG.is_file():
        print(f"Config already exists: {USERSPACE_CONFIG}")
        return 0
    if not PLUGIN_CONFIG.is_file():
        print(f"ERROR: Plugin default config not found: {PLUGIN_CONFIG}", file=sys.stderr)
        return 1
    USERSPACE_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    content = PLUGIN_CONFIG.read_text()
    detected_cache = _detect_plugin_cache()
    content = content.replace(
        "~/.claude/plugins/cache/Dev10x-Guru/dev10x-claude",
        detected_cache,
    )
    USERSPACE_CONFIG.write_text(content)
    print(f"Created: {USERSPACE_CONFIG}")
    print(f"Plugin cache: {detected_cache}")
    print("Edit this file to add your project roots.")
    return 0
