#!/usr/bin/env bash
# Generate two files from skill directories:
#   ~/.claude/SKILLS.md         — flat list for humans and AI context
#   ~/.claude/.skills-motd.txt  — tree with dependencies for terminal MOTD
# Default: skip if both outputs are newer than all SKILL.md files.
# Pass --force to always regenerate.
set -euo pipefail

SKILLS_DIR="${HOME}/.claude/skills"
SKILLS_MD="${HOME}/.claude/SKILLS.md"
MOTD="${HOME}/.claude/.skills-motd.txt"

if [[ "${1:-}" != "--force" ]]; then
    needs_regen=0
    for out in "$SKILLS_MD" "$MOTD"; do
        if [[ ! -f "$out" ]]; then
            needs_regen=1; break
        fi
        stale=$(find "$SKILLS_DIR" -maxdepth 2 -name 'SKILL.md' -newer "$out" 2>/dev/null | head -1)
        [[ -n "$stale" ]] && { needs_regen=1; break; }
    done
    [[ $needs_regen -eq 0 ]] && exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPS_FILE="${SCRIPT_DIR}/dependencies.txt"

declare -A DEPS
if [[ -f "$DEPS_FILE" ]]; then
    while IFS='|' read -r dep_skill dep_list; do
        [[ "$dep_skill" =~ ^#|^$ ]] && continue
        DEPS["$dep_skill"]=$(echo "$dep_list" | tr ',' '\n' | sort | paste -sd',' -)
    done < "$DEPS_FILE"
fi

declare -A DESC INV
names_file=$(mktemp)
trap 'rm -f "$names_file"' EXIT

for skill_dir in "$SKILLS_DIR"/*/; do
    sf="${skill_dir}SKILL.md"
    [[ -f "$sf" ]] || continue

    name="" desc="" invocable="false"
    in_fm=0 grab_desc=0

    while IFS= read -r line; do
        [[ "$line" == "---" ]] && { in_fm=$((in_fm + 1)); [[ $in_fm -ge 2 ]] && break; continue; }
        [[ $in_fm -lt 1 ]] && continue

        if [[ $grab_desc -eq 1 ]]; then
            if [[ "$line" =~ ^[[:space:]] ]]; then
                desc="${line#"${line%%[![:space:]]*}"}"
                grab_desc=0; continue
            fi
            grab_desc=0
        fi

        case "$line" in
            name:*) name="${line#name:}"; name="${name# }" ;;
            description:*\>*|description:*\|*) grab_desc=1 ;;
            description:*) desc="${line#description:}"; desc="${desc# }" ;;
            user-invocable:*true*) invocable="true" ;;
        esac
    done < "$sf"

    [[ -z "$name" ]] && name=$(basename "$skill_dir")
    desc="${desc#\"}"; desc="${desc%\"}"
    desc="${desc#\'}"; desc="${desc%\'}"
    [[ ${#desc} -gt 55 ]] && desc="${desc:0:52}..."

    DESC["$name"]="$desc"
    INV["$name"]="$invocable"
    echo "$name" >> "$names_file"
done

total=$(wc -l < "$names_file")
inv_count=0
for n in "${!INV[@]}"; do
    [[ "${INV[$n]}" == "true" ]] && inv_count=$((inv_count + 1))
done

col=28

skill_label() {
    local prefix="$1" name="$2" sep=""
    [[ -n "$prefix" ]] && sep=" "
    if [[ "${INV[$name]:-false}" == "true" ]]; then
        printf '%s%s/%s' "$prefix" "$sep" "$name"
    else
        printf '%s%s %s' "$prefix" "$sep" "$name"
    fi
}

render_line() {
    local prefix="$1" name="$2"
    printf "%-${col}s %s\n" "$(skill_label "$prefix" "$name")" "${DESC[$name]:-}"
}

# ── SKILLS.md: flat list for humans + AI context ─────────────
{
    printf '%s skills, %s invocable\n' "$total" "$inv_count"
    sort "$names_file" | while read -r name; do
        render_line "" "$name"
    done
} > "$SKILLS_MD"

# ── .skills-motd.txt: tree with deps for terminal ────────────
{
    printf '%s skills, %s invocable\n' "$total" "$inv_count"

    sort "$names_file" | while read -r name; do
        render_line "" "$name"

        [[ -z "${DEPS[$name]:-}" ]] && continue
        IFS=',' read -ra deps <<< "${DEPS[$name]}"
        last=$((${#deps[@]} - 1))

        for i in "${!deps[@]}"; do
            dep="${deps[$i]}"
            if [[ $i -eq $last ]]; then
                render_line "└─" "$dep"
                cont="   "
            else
                render_line "├─" "$dep"
                cont="│  "
            fi

            [[ -z "${DEPS[$dep]:-}" ]] && continue
            IFS=',' read -ra subs <<< "${DEPS[$dep]}"
            sub_last=$((${#subs[@]} - 1))

            for j in "${!subs[@]}"; do
                sub="${subs[$j]}"
                if [[ $j -eq $sub_last ]]; then
                    render_line "${cont}└─" "$sub"
                else
                    render_line "${cont}├─" "$sub"
                fi
            done
        done
    done
} > "$MOTD"

echo "Generated SKILLS.md + .skills-motd.txt ($total skills, $inv_count invocable)"
