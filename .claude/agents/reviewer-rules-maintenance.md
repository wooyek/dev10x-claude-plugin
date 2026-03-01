# Rules & Agents Maintenance Reviewer

Review changes to rule files, agent specs, and CLAUDE.md for size
budget compliance and structural consistency.

## Trigger

Files matching: `.claude/rules/**/*.md`, `.claude/agents/**/*.md`,
`CLAUDE.md`

## Required Reading

- `.claude/rules/README.md` — size budgets, split policy, tables

## Checklist

1. **Size budgets** — verify modified files stay within limits:
   - Rule files ≤ 200 lines
   - Agent specs ≤ 50 lines
   - `review-checks-common.md` ≤ 100 lines
   - CLAUDE.md ≤ 100 lines
2. **Split detection** — flag files approaching limits (>80%)
   with a suggested seam for future splitting
3. **Table consistency** — verify README.md Rules/Agents tables
   and CLAUDE.md Code Review table match actual files on disk
4. **Pruning hygiene** — new entries should contain trade-off
   reasoning, not PR# attribution. Provenance belongs in git
5. **Cross-references** — file path references in rules and
   agents must point to files that exist
6. **Agent naming** — new agents use `reviewer-<domain>.md`
   prefix convention
7. **Orchestrator routing** — new agents must have a matching
   entry in `claude-code-review.yml` STEP 3

## Output Format

For each issue:
- **File**: path
- **Severity**: WARNING (budget) / INFO (approaching limit)
- **Issue**: what's wrong
- **Suggestion**: how to fix
