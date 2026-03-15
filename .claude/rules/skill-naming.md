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

*Why?* This is an intentional **branding decision**. Claude Code
auto-constructs `<PluginName>:<dir-name>` identifiers for the
system-reminder listing (e.g., `Dev10x:git-commit`), so the prefix
is technically redundant for skill resolution. However, we include
it explicitly in `name:` for:
- **Brand consistency** — the `dev10x:` prefix is visible in MOTD
  listings and `Skill()` invocations across all projects
- **Collision avoidance** — explicit prefix prevents ambiguity when
  multiple plugins define similarly-named skills
- **Self-documenting** — skill identity is clear without needing
  plugin context

Note: official plugins (superpowers, svelte, hookify) omit the
prefix and rely on auto-construction. Our explicit prefix is a
deliberate divergence for branding.

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

## `invocation-name` field

**Required on every skill.** The `invocation-name:` field makes
skills available for invocation. By default it MUST match `name:`:

```yaml
name: dev10x:git-commit
invocation-name: dev10x:git-commit
```

The `invocation-name:` MUST match `name:` — no exceptions. Both
fields carry the `dev10x:` prefix for brand consistency.

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
- **Invocation**: `dev10x:` prefix → branding + namespace isolation
- **`invocation-name:`**: required on every skill, matches `name:` by default
- **Families**: prefix groups for tab-completion discoverability
- **Evals**: structured JSON placed in fixed directory with prefixed `skill_name`
