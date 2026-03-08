# Skill Orchestration: Formatting as Intent Signal

Markdown formatting controls how Claude agents interpret task
specifications. This guide clarifies the distinction between mandatory
and advisory patterns in skill definitions.

## Numbered Lists = Instructions

When a skill's Orchestration section lists multiple `TaskCreate` or
`TaskUpdate` calls in a **numbered list**, they are interpreted as
blocking requirements that must execute before other work begins.

**Pattern:**
```markdown
**REQUIRED: Create tasks before ANY work.** Execute these
`TaskCreate` calls at startup:

1. `TaskCreate(subject="Step 1", activeForm="Working on Step 1")`
2. `TaskCreate(subject="Step 2", activeForm="Working on Step 2")`
```

**Effect:** Agents read numbered lists as ordered instructions and
execute them sequentially.

## Code Blocks = Examples Only

When the same task specifications appear in a **fenced code block**
(triple backticks), they are interpreted as illustrative examples,
not mandatory requirements.

**Anti-pattern:**
```markdown
**Task tracking:** Create tasks for each step:

\`\`\`
TaskCreate(subject="Step 1", activeForm="Working on Step 1")
TaskCreate(subject="Step 2", activeForm="Working on Step 2")
\`\`\`
```

**Effect:** Agents may skip code-block instructions, treating them as
non-binding examples.

## Enforcement Language

Pair numbered lists with explicit intent markers to remove ambiguity:

| Marker | Usage | Rationale |
|--------|-------|-----------|
| `REQUIRED:` | Tasks that block all downstream work | Highest precedence |
| `MANDATORY:` | Non-negotiable setup steps | Policy/constraint |
| `ALWAYS` | Repeating conditions across phases | Consistency |
| `DO NOT SKIP` | Steps with critical side effects | Safety |

**Example:**
```markdown
**REQUIRED: Create tasks before ANY work.** Execute these
`TaskCreate` calls at startup:

1. `TaskCreate(subject="Verify state", activeForm="Verifying")`
```

## Why Formatting Matters

Claude agents process Markdown structure as semantic information:
- **Numbered lists** trigger sequential-instruction parsing
- **Code blocks** trigger example/illustration parsing
- **Intent markers** add explicit constraints to the prompt context

This distinction arises naturally from Claude's instruction processing,
not from explicit code changes.

## Migration Example

**Before (code block—reads as example):**
```markdown
When writing multi-step skills, include task tracking:

\`\`\`
TaskCreate(subject="Phase 1: Gather", activeForm="Gathering")
TaskCreate(subject="Phase 2: Plan", activeForm="Planning")
\`\`\`
```

**After (numbered list + REQUIRED):**
```markdown
**REQUIRED: Create tasks before ANY work.** Execute these
`TaskCreate` calls at startup:

1. `TaskCreate(subject="Phase 1: Gather", activeForm="Gathering")`
2. `TaskCreate(subject="Phase 2: Plan", activeForm="Planning")`
```

## Reference

See `references/task-orchestration.md` for full orchestration patterns,
including auto-advance, batched decisions, and tier guidance.

See `.claude/agents/reviewer-skill.md` item 14a for review checklist
enforcement of this pattern.
