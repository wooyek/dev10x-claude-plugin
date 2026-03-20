#!/usr/bin/env bash
# SessionStart hook
# Checks if git branch-comparison aliases are configured.
# Reports available aliases so the agent uses them instead of
# $(git merge-base ...) subshells that break permission matching.

set -euo pipefail

ALIASES=(develop-log develop-diff develop-rebase autosquash-develop development-log development-diff development-rebase autosquash-development trunk-log trunk-diff trunk-rebase autosquash-trunk main-log main-diff main-rebase autosquash-main master-log master-diff master-rebase autosquash-master)

missing=()
present=()

for alias in "${ALIASES[@]}"; do
    if git config --get "alias.${alias}" >/dev/null 2>&1; then
        present+=("$alias")
    else
        missing+=("$alias")
    fi
done

if [[ ${#missing[@]} -eq 0 ]]; then
    echo "Git aliases available: ${present[*]}"
    echo "Use \`git {base}-log\`, \`git {base}-diff\`, \`git {base}-rebase\`"
    echo "instead of \$(git merge-base ...) to avoid permission prompts."
else
    echo "Git aliases missing: ${missing[*]}"
    if [[ ${#present[@]} -gt 0 ]]; then
        echo "Git aliases available: ${present[*]}"
    fi
    echo "Run the git-alias-setup skill (/Dev10x:git-alias-setup) to configure them."
fi
