# Skill Rename Design

Reorganize skill directory and invocation names for consistency,
discoverability, and future-proofing.

## Constraints

- `dx:` namespace prefix stays on all invocation names
- Directory names never contain `dx:` or colons
- One colon per invocation name (`dx:<name>`, no nesting)
- `gh-` platform prefix preserved for GitHub-specific skills
  (future-proofs for `gl-` GitLab family)
- Family prefix on invocations enables tab-completion discovery

## Families

| Family | Prefix | Count | Domain |
|---|---|---|---|
| `gh-pr-*` | `gh-` | 9 | GitHub pull request lifecycle |
| `git-*` | `git-` | 7 | Platform-agnostic git operations |
| `park-*` | `park-` | 4 | Deferral / parking lot |
| `session-*` | `session-` | 2 | Active work + session lifecycle |
| `skill-*` | `skill-` | 3 | Skill meta-tooling |
| standalone | — | 3 | `jtbd`, `linear`, `py-uv` |

## Changes (12 of 28 skills)

| Current Dir | New Dir | Current Invoke | New Invoke | Rationale |
|---|---|---|---|---|
| `gh` | `gh-context` | `dx:gh` | `dx:gh-context` | Bare name reveals nothing; skill resolves PR context |
| `gh-pr-comment-fixup` | `gh-pr-fixup` | `dx:gh-pr-comment-fixup` | `dx:gh-pr-fixup` | "comment" redundant — fixups are always for comments |
| `git-branch-groom` | `git-groom` | `dx:git-branch-groom` | `dx:git-groom` | "branch" implied — grooming is always branch history |
| `ticket-from-commit` | `git-promote` | `dx:ticket:from-commit` | `dx:git-promote` | Moves to git family; "promote" = extract commit into tracked work |
| `tasks-defer` | `park` | `dx:defer` | `dx:park` | New family; "park" metaphor for deferral routing |
| `tasks-todo` | `park-todo` | `dx:todo` | `dx:park-todo` | Family prefix for discoverability |
| `tasks-remind` | `park-remind` | `dx:remind` | `dx:park-remind` | Family prefix for discoverability |
| `tasks-discover` | `park-discover` | `dx:discover` | `dx:park-discover` | Family prefix for discoverability |
| `tasks` | `session-tasks` | `dx:tasks` | `dx:session-tasks` | Scopes generic "tasks" to session context |
| `tasks-wrap-up` | `session-wrap-up` | `dx:wrap-up` | `dx:wrap-up` | Dir moves to session family; invoke stays short |
| `skill-motd` | `skill-index` | `dx:skill-motd` | `dx:skill-index` | "index" describes purpose; "MOTD" is Unix jargon |

## Unchanged (16 skills)

| Dir | Invoke |
|---|---|
| `gh-pr-bookmark` | `dx:gh-pr-bookmark` |
| `gh-pr-create` | `dx:gh-pr-create` |
| `gh-pr-monitor` | `dx:gh-pr-monitor` |
| `gh-pr-request-review` | `dx:gh-pr-request-review` |
| `gh-pr-respond` | `dx:gh-pr-respond` |
| `gh-pr-review` | `dx:gh-pr-review` |
| `gh-pr-triage` | `dx:gh-pr-triage` |
| `git` | `dx:git` |
| `git-commit` | `dx:git-commit` |
| `git-commit-split` | `dx:git-commit-split` |
| `git-fixup` | `dx:git-fixup` |
| `git-worktree` | `dx:git-worktree` |
| `jtbd` | `dx:jtbd` |
| `linear` | `dx:linear` |
| `py-uv` | `dx:py-uv` |
| `skill-audit` | `dx:skill-audit` |
| `skill-create` | `dx:skill-create` |

## Final Filesystem

```
skills/
├── gh-context/           ← gh/
├── gh-pr-bookmark/
├── gh-pr-create/
├── gh-pr-fixup/          ← gh-pr-comment-fixup/
├── gh-pr-monitor/
├── gh-pr-request-review/
├── gh-pr-respond/
├── gh-pr-review/
├── gh-pr-triage/
├── git/
├── git-commit/
├── git-commit-split/
├── git-fixup/
├── git-groom/            ← git-branch-groom/
├── git-promote/          ← ticket-from-commit/
├── git-worktree/
├── jtbd/
├── linear/
├── park/                 ← tasks-defer/
├── park-discover/        ← tasks-discover/
├── park-remind/          ← tasks-remind/
├── park-todo/            ← tasks-todo/
├── py-uv/
├── session-tasks/        ← tasks/
├── session-wrap-up/      ← tasks-wrap-up/
├── skill-audit/
├── skill-create/
└── skill-index/          ← skill-motd/
```

## Implementation Notes

Each rename requires updating:
1. Directory name (`git mv`)
2. `name:` field in SKILL.md
3. `description:` field references to old name
4. Cross-references in other skills that delegate to renamed skills
5. User-level skill symlinks in `~/.claude/skills/`
6. Hook scripts that reference skill paths
7. `.claude/rules/skill-naming.md` abbreviated names table
8. MOTD generation (re-run `dx:skill-index` after all renames)
