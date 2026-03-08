# Skill Implementation Patterns

The codebase supports two distinct skill patterns. Review expectations differ
based on which pattern a skill uses.

## Pattern 1: Script-Based Skills

Directory contains `scripts/` with executable implementations.

**Characteristics**:
- SKILL.md provides overview and usage
- Actual implementation in `scripts/` (shell, Python, etc.)
- Examples: `gh-pr-create`, `git-commit`, `git-groom`

**Reviewer expectations** (from `reviewer-skill.md`):
- Items 4, 5, 6: Script existence, permissions, error handling
- Item 8: `allowed-tools` must declare `Bash(...)` entries
- Item 32: Output format validation

**Flag as CRITICAL if missing**: Actual implementation scripts

## Pattern 2: Orchestration-Based Skills

Directory contains only SKILL.md; Claude interprets and executes the workflow.

**Characteristics**:
- SKILL.md documents a multi-step workflow
- Claude reads and executes each step
- External tools called via `allowed-tools` declarations
- Examples: `gh-pr-request-review`, `park`

**Reviewer expectations** (from `reviewer-skill.md`):
- Items 4, 5: Do NOT apply (no scripts expected)
- Item 8: **Critical** — all external tool calls must be in `allowed-tools`
- Items 15c, 19: Config schema and decision gate enforcement
- Item 14a: Orchestration list formatting in SKILL.md

**Flag as CRITICAL if missing**: `allowed-tools` declarations for external
tools or decision gates; will cause per-invocation approval prompts.

## Pattern Detection

Determine which pattern applies:
1. Check if skill directory contains `scripts/` subdirectory
   - Yes → Script-based; apply Items 4, 5, 6, 32
   - No → Continue to step 2
2. Check if SKILL.md references local paths like `${CLAUDE_PLUGIN_ROOT}/skills/...`
   - Yes → Script-based; likely missing scripts directory
   - No → Proceed to step 3
3. Check if SKILL.md references external binaries or `~/.claude/tools/` only
   - Yes + no `scripts/` → Orchestration-based; Items 4, 5 do NOT apply
   - No → Ambiguous; flag as INFO for author clarification

## Evals for Skills with Decision Gates

Skills with decision gates (marked `REQUIRED: Call AskUserQuestion` in SKILL.md)
must include `evals/evals.json`:

- **Field names** must match `references/eval-schema.md`: `setup`, `checks`,
  `type`, `assertion`, `signal` (not `check`, `assertions`, or other variations)
- **Gate coverage**: Count gates in SKILL.md and verify evals include assertions
  for ALL gates, including branch-conditional gates (create separate scenarios
  if needed)
- **Schema example**: Point to a well-formed evals file in an existing skill
  when asking authors; naming is non-obvious

Refer to `references/eval-schema.md` for complete format and examples.
