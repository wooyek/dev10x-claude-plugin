---
name: dev10x:playbook
description: >
  View and customize playbooks (step-by-step procedures) for any
  orchestration skill. List playbook-powered skills, inspect plays,
  edit steps through a guided flow, or reset to defaults.
user-invocable: true
invocation-name: dev10x:playbook
allowed-tools:
  - Read(~/.claude/projects/**/memory/playbooks/*.yaml)
  - Write(~/.claude/projects/**/memory/playbooks/*.yaml)
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
---

# dev10x:playbook — Playbook Manager

## Overview

A **playbook** is a reusable, customizable set of steps that an
orchestration skill follows. Any skill can become playbook-powered
by placing a `references/playbook.yaml` in its directory.

This skill provides a guided interface for viewing and customizing
playbooks so users never need to edit raw YAML.

### Discovery

A skill is playbook-powered when it has:
```
skills/<skill-name>/references/playbook.yaml
```

This convention requires no front matter changes — the file's
presence is sufficient.

### Storage

Each skill's user overrides live in a separate file:
```
~/.claude/projects/<project>/memory/playbooks/<skill-key>.yaml
```

Where `<skill-key>` is the skill directory name (e.g., `work-on`,
`tt-e2e-debug`). This keeps overrides isolated per skill.

### Resolution Order

When loading a play, resolve in this order:
1. User overrides (`persist: false`) — use once, then remove
2. User overrides (`persist: true`) — reuse across sessions
3. Defaults from the skill's `references/playbook.yaml`

## Orchestration

**REQUIRED: Create a task at invocation.** Execute at startup:

1. `TaskCreate(subject="Manage playbooks", activeForm="Managing playbooks")`

Mark completed when done: `TaskUpdate(taskId, status="completed")`

## Subcommands

Parse the arguments to determine the subcommand:

| Arguments | Subcommand | Action |
|-----------|-----------|--------|
| (none) or `list` | List | Show all playbook-powered skills |
| `view <skill> [<play>]` | View | Show plays for a skill (or one play) |
| `edit <skill> <play>` | Edit | Guided editing of a play |
| `reset [<skill> [<play>]]` | Reset | Reset overrides to defaults |

If `<skill>` is ambiguous, match against both directory name and
invocation name (e.g., `work-on` matches `dev10x:work-on`).

---

## Subcommand: List

Scan all installed skill directories for `references/playbook.yaml`.

**Steps:**

1. Glob for `${CLAUDE_PLUGIN_ROOT}/skills/*/references/playbook.yaml`
   and any other plugin skill directories
2. For each found, read the YAML to count plays and get descriptions
3. Read user override files to detect customizations
4. Display:

```
## Playbook-Powered Skills

| Skill | Plays | Customized? |
|-------|-------|-------------|
| dev10x:work-on | 5 (feature, bugfix, pr-continuation, local-only, investigation) | feature ✎ |
| tt:e2e-debug | 2 (investigate, fix) | — |

Use `/dev10x:playbook view <skill>` to inspect plays.
Use `/dev10x:playbook edit <skill> <play>` to customize.
```

---

## Subcommand: View

Show plays for a specific skill, or drill into one play.

**Steps:**

1. Locate the skill's `references/playbook.yaml`
2. Read it and any user overrides
3. If `<play>` specified: show that play's full step tree
4. If no `<play>`: show a summary of all plays in the skill

**Play detail format:**

```
## dev10x:work-on → feature

**Prompt:** Use when a ticket describes new functionality...

| # | Type | Step | Skills | Children |
|---|------|------|--------|----------|
| 1 | detailed | Set up workspace | dev10x:ticket-branch | — |
| 2 | detailed | Draft Job Story | dev10x:jtbd | — |
| 3 | epic | Design implementation approach | — | 3 children |
|   |   | ├─ Read relevant code | — | |
|   |   | ├─ Identify affected components | — | |
|   |   | └─ Propose approach | — | |
| ... | | | | |

**Source:** defaults (no user override)
```

If an override exists, show both so the user can compare.

---

## Subcommand: Edit

Guided editing of a play. Users describe changes in natural
language rather than editing YAML.

**Steps:**

1. Show the current play (same as View)
2. **REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
   Options:
   - **Add step** — Insert a new step at a specific position
   - **Remove step** — Remove a step by number
   - **Reorder steps** — Move a step to a different position
   - **Edit step** — Change a step's subject, type, prompt, or skills

3. Based on the user's choice, gather details:

   **Add step:**
   - Ask: position (before/after which step), subject, type
     (detailed/epic), skills (optional), prompt (optional)
   - If epic: ask if it should have pre-templated children

   **Remove step:**
   - Confirm which step to remove (by number)
   - Warn if removing a step that other skills depend on

   **Reorder steps:**
   - Ask which step to move and where

   **Edit step:**
   - Show the current step details
   - Ask what to change

4. Preview the modified play as a numbered tree
5. **REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
   Options:
   - **Save** — Write the override to the user's playbook file
   - **Continue editing** — Make more changes (loop back to step 2)
   - **Discard** — Abandon changes

6. If Save:
   - Read the user's playbook file for this skill (create if absent)
   - Add/update the override entry for this play
   - Set `persist: true` and `added: <today's date>`
   - Write to `~/.claude/projects/<project>/memory/playbooks/<skill-key>.yaml`

**Override format:**

```yaml
overrides:
  - play: feature
    persist: true
    added: 2026-03-11
    steps:
      - subject: Set up workspace
        type: detailed
        skills: [dev10x:ticket-branch]
      # ... full step list
```

---

## Subcommand: Reset

Reset overrides to the skill's default playbook.

**Steps:**

1. If `<skill>` and `<play>` specified: reset that one play
2. If only `<skill>`: reset all overrides for that skill
3. If neither: show all overrides across all skills
4. **REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
   Options:
   - **Reset** — Remove the selected override(s)
   - **Cancel** — Keep current overrides

---

## Playbook YAML Schema

Each skill's `references/playbook.yaml` follows this structure:

```yaml
# Top-level: map of play names to play definitions
defaults:
  <play-name>:
    prompt: >
      Heuristic guidance for when this play applies and
      how to adapt it based on context.
    steps:
      - subject: Step title (required)
        type: detailed | epic (required)
        prompt: >
          Expansion guidance for the agent executing
          this step (optional)
        skills: [skill1, skill2] (optional)
        steps: [] (optional — pre-templated epic children)
        condition: hint (optional)

overrides: []  # populated by this skill when user customizes
```

See `references/playbook.yaml` for the full work-on playbook
with all 5 plays as a reference implementation.

## How to Make a Skill Playbook-Powered

1. Create `skills/<your-skill>/references/playbook.yaml`
2. Define one or more plays with steps following the schema above
3. In your SKILL.md orchestration section, load the playbook:
   ```
   1. Read user overrides from
      ~/.claude/projects/<project>/memory/playbooks/<skill-key>.yaml
   2. Fall back to references/playbook.yaml
   3. Create TaskCreate per step in the resolved play
   ```
4. The `dev10x:playbook` skill automatically discovers your skill

**Loading pattern for orchestration skills:**
```
Read(~/.claude/projects/<project>/memory/playbooks/<key>.yaml)
  → if absent, Read(${CLAUDE_PLUGIN_ROOT}/skills/<skill>/references/playbook.yaml)
  → resolve: overrides first, then defaults
  → create tasks from steps
```

## Integration with Orchestration Skills

Any orchestration skill can load its playbook using the resolution
order above. When presenting the play to the user, it should note:
"Customize this playbook with `/dev10x:playbook edit <skill> <play>`."

If a user asks to customize during an active session, the
orchestrator can delegate to this skill mid-flight and then
reload the updated playbook.

---

## Examples

### Example 1: List all playbook-powered skills

**User:** `/dev10x:playbook`

Shows all skills with `references/playbook.yaml`, their play
counts, and customization status.

### Example 2: View work-on plays

**User:** `/dev10x:playbook view work-on`

Shows summary of all 5 plays (feature, bugfix, etc.) with
step counts and descriptions.

### Example 3: View a specific play

**User:** `/dev10x:playbook view work-on bugfix`

Shows the full bugfix play with all steps, children, prompts,
and skill delegations in a readable tree format.

### Example 4: Customize a play for a project

**User:** `/dev10x:playbook edit work-on feature`

1. Shows current feature play (10 steps)
2. User selects "Add step"
3. User says: "Add a 'Run e2e tests' step after Verify"
4. Skill creates the step with `skills: [tt:e2e-debug]`
5. Shows preview with 11 steps
6. User selects "Save"
7. Writes override to `~/.claude/projects/.../memory/playbooks/work-on.yaml`

### Example 5: Future — e2e-debug with a playbook

Once `tt:e2e-debug` adds `references/playbook.yaml`:
```yaml
defaults:
  investigate:
    prompt: >
      Use when an e2e test failure needs root cause analysis.
    steps:
      - subject: Fetch CI run artifacts
        type: detailed
        prompt: Download screenshots, logs, and video from the failed run.
      - subject: Analyze failure pattern
        type: epic
        prompt: Compare against known flaky patterns and recent changes.
      - subject: Propose fix or report
        type: detailed
        prompt: Either implement a fix or document findings.
```

Then `/dev10x:playbook view tt-e2e-debug investigate` works
automatically — no changes to this skill needed.
