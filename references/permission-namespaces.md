# Permission Namespaces

Central registry of `/tmp/claude/<namespace>/` directories used by Dev10x skills.

## Namespace Registry

| Namespace | Used by | Purpose | Introduced |
|-----------|---------|---------|---|
| `git` | git-commit, git-groom, git-rebase-groom, git-worktree | Commit messages, rebase state, worktree metadata | PR #126 (GH-120) |
| `review` | gh-pr-review, code-reviewer agent | PR review comments, thread state | PR #893 (GH-878) |
| `skill-audit` | skill-audit skill | Skill analysis results, permissions dump | PR #893 (GH-878) |
| `playwright` | playwright skill | Test run output, screenshots | PR #893 (GH-878) |
| `self-qa` | self-qa skill | Evidence screenshots, test logs | PR #893 (GH-878) |
| `ticket-scope` | ticket-scope skill | Issue context, JIRA/Linear data | PR #893 (GH-878) |
| `slack` | slack-review-request skill | Slack message payloads | PR #893 (GH-878) |
| `pr-monitor` | gh-pr-monitor skill | PR state snapshots, CI logs | PR #893 (GH-878) |
| `gh` | gh-pr-create, gh-context skills | GitHub API responses | PR #893 (GH-878) |

## Adding a New Namespace

When a skill creates temp files under a new `/tmp/claude/<ns>/` namespace:

1. Add the namespace to this registry table
2. Add RWE (read/write/execute) permissions to
   `skills/upgrade-cleanup/projects.yaml` § Temp file namespaces
3. Update the skill's SKILL.md `allowed-tools:` to include the namespace path
4. File PR against this document and `projects.yaml` together

## Validation

To verify all namespaces are registered:

```bash
grep -r 'mktmp.*--namespace' skills/ | cut -d: -f2 | grep -o '\-\-namespace\s\+[a-z-]*' | awk '{print $2}' | sort -u
```

Output should match namespaces listed above.
