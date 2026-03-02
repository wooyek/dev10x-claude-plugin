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

Use the `dx:<feature-name>` format in the SKILL.md front matter.

**Good:**
```yaml
name: dx:git-worktree
name: dx:skill-audit
name: dx:park
```

**Bad:**
```yaml
name: git-worktree
name: skill-audit
```

*Why?* The `dx:` namespace prefix identifies this plugin's skills
at invocation time. Without it, skills could collide with skills
from other plugins or built-in commands.

## Family Naming

Skills use family prefixes for tab-completion discoverability:

| Directory         | Invocation name      |
|-------------------|----------------------|
| `park/`           | `dx:park`            |
| `park-todo/`      | `dx:park-todo`       |
| `park-remind/`    | `dx:park-remind`     |
| `park-discover/`  | `dx:park-discover`   |
| `session-tasks/`  | `dx:session-tasks`   |
| `session-wrap-up/`| `dx:wrap-up`         |
| `ticket-branch/`  | `dx:ticket-branch`   |
| `ticket-create/`  | `dx:ticket-create`   |
| `ticket-jtbd/`    | `dx:ticket-jtbd`     |
| `ticket-scope/`   | `dx:ticket-scope`    |

Other skills use the full directory name: `dx:git-worktree`,
`dx:skill-audit`, `dx:skill-create`.

## `invocation-name` vs `name`

`name:` is the canonical plugin-registered invocation and MUST use the
`dx:` prefix. `invocation-name:` is an optional alias and MAY use an
alternative namespace when the skill bridges to an external skill family:

| `name:`           | `invocation-name:` | Use case                             |
|-------------------|--------------------|--------------------------------------|
| `dx:ticket-jtbd`  | `ticket:jtbd`      | Cross-family alias for ticket skills |
| `dx:git-promote`  | `dx:git-promote`   | Redundant (harmless)                 |

Do NOT flag `invocation-name:` with a non-`dx:` prefix as a naming
violation when `name:` already carries the correct `dx:` prefix.

## Rationale Summary

- **Directory**: plain name → clean filesystem, no redundant prefix
- **Invocation**: `dx:` prefix → namespace isolation at call time
- **Families**: prefix groups for tab-completion discoverability
