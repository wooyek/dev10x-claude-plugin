---
paths:
  - "skills/**"
---

# Skill Naming Convention

Rules for naming skill directories and invocation names in
this plugin.

## Directory Names

Use the plain feature name. No `dx-` prefix on directories.

**Good:**
```
skills/git-worktree/
skills/skill-audit/
skills/park/
skills/linear/
```

**Bad:**
```
skills/dx-git-worktree/
skills/dx-skill-audit/
```

*Why?* The filesystem already scopes skills to this plugin's
`skills/` directory. Adding a redundant prefix clutters tab
completion and directory listings.

## Invocation Name (SKILL.md `name:` field)

**Deprecated:** The `dx:` prefix was superseded by `dev10x:` as of commit 44c0dd8.
All new skills must use the `dev10x:` namespace; old `dx:` references are no longer recognized.

Use the `dev10x:<feature-name>` format in the SKILL.md front matter.

**Good:**
```yaml
name: dev10x:git-worktree
name: dev10x:skill-audit
name: dev10x:park
```

**Bad:**
```yaml
name: git-worktree
name: skill-audit
```

*Why?* The `dev10x:` namespace prefix identifies this plugin's skills
at invocation time. Without it, skills could collide with skills
from other plugins or built-in commands.

## Family Naming

Skills use family prefixes for tab-completion discoverability:

| Directory         | Invocation name      |
|-------------------|----------------------|
| `park/`           | `dev10x:park`            |
| `park-todo/`      | `dev10x:park-todo`       |
| `park-remind/`    | `dev10x:park-remind`     |
| `park-discover/`  | `dev10x:park-discover`   |
| `session-tasks/`  | `dev10x:session-tasks`   |
| `session-wrap-up/`| `dev10x:wrap-up`         |
| `ticket-branch/`  | `dev10x:ticket-branch`   |
| `ticket-create/`  | `dev10x:ticket-create`   |
| `ticket-jtbd/`    | `dev10x:ticket-jtbd`     |
| `ticket-scope/`   | `dev10x:ticket-scope`    |

Other skills use the full directory name: `dev10x:git-worktree`,
`dev10x:skill-audit`, `dev10x:skill-create`.

## `invocation-name` vs `name`

`name:` is the canonical plugin-registered invocation and MUST use the
`dev10x:` prefix. `invocation-name:` is an optional alias and MAY use an
alternative namespace when the skill bridges to an external skill family:

| `name:`           | `invocation-name:` | Use case                             |
|-------------------|--------------------|--------------------------------------|
| `dev10x:ticket-jtbd`  | `ticket:jtbd`      | Cross-family alias for ticket skills |
| `dev10x:git-promote`  | `dev10x:git-promote`   | Redundant (harmless)                 |

Do NOT flag `invocation-name:` with a non-`dev10x:` prefix as a naming
violation when `name:` already carries the correct `dev10x:` prefix.

## Eval Criteria Files

Eval criteria define measurable dimensions and test scenarios for skills.

**Structure:** Place all evals in `skills/<feature-name>/evals/evals.json`
- Directory name: plain feature name (no `dev10x-` prefix)
- Filename: fixed as `evals.json` (not `dev10x-evals.json`)
- Inside file: `skill_name` field MUST use `dev10x:` prefix

**Schema:** See `references/eval-criteria.md` for full structure.

**Example:**
```json
{
  "skill_name": "dev10x:git-commit",
  "eval_dimensions": [...],
  "evals": [...]
}
```

**Note:** Eval files are schema/documentation only, not code.
They do not require executable permissions or script references.

## Rationale Summary

- **Directory**: plain name → clean filesystem, no redundant prefix
- **Invocation**: `dev10x:` prefix → namespace isolation at call time
- **Families**: prefix groups for tab-completion discoverability
- **Evals**: structured JSON placed in fixed directory with prefixed `skill_name`
