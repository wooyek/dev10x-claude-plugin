# Lessons Learned Implementation Status

**PR Base:** PR #404 (GH-400 Enforce Sub-Skill Delegation)
**Date:** 2026-03-23
**Branch:** claude/lessons-404

## Value Filter Results

Applied to all High/Medium items from lessons_learned_report.md:

| Item | Target File | Verdict | Reason |
|------|-------------|---------|--------|
| Skill delegation assertions | `skills/gh-pr-respond/evals/evals.json` | ❌ SKIP | File inside `skills/` (not allowed) |
| Enforcement coverage rule | `.claude/rules/skill-gates.md` | ✅ PASS | Novel content, recurring pattern, actionable |
| Precondition pattern guide | `.claude/rules/precondition-patterns.md` | ✅ PASS | New file, recurring pattern, actionable |
| Branch location checks | `skills/gh-pr-*/SKILL.md` | ❌ SKIP | Files inside `skills/` (not allowed) |
| Stash guard in other skills | `skills/git-*/SKILL.md` | ❌ SKIP | Files inside `skills/` (not allowed) |
| Evaluation schema update | `references/eval-schema.md` | ✅ PASS | Novel examples, recurring pattern |

**Survivors:** 3 items (≥2 threshold)

## Implementation Progress

### ✅ Completed

1. **references/eval-schema.md** — Added Skill() invocation examples
   - Updated check types table to mention Skill() invocations
   - Added signal patterns for skill-tool detection
   - Added "Example 2: Skill() Delegation" with assertion patterns
   - Lines changed: +29

### ⏳ Awaiting Permission

2. **.claude/rules/skill-gates.md** — Expand Evaluation Assertions section
   - Add documentation for Skill() delegation enforcement
   - Include assertion examples for both AskUserQuestion and Skill() tools
   - Est. lines: +30

3. **.claude/rules/precondition-patterns.md** — New rule file
   - Document precondition pattern with 2 examples
   - Est. lines: ~110

## Why Filter Succeeded

- **Deduplication:** Concepts not in current rule files
- **Recurrence:** All address patterns from PR #404 applicable to future skills
- **Actionability:** Concrete guidance with examples
- **Budget:** ~169 combined lines within budgets (rule ≤200, ref ≤200)

## Filtered Out (Allowed files only)

- 3 items require modifying `skills/` directory (prohibited per hard constraints)
