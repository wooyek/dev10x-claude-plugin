# Implementation Changes for PR #388 Lessons Learned

## Summary
This document describes the changes that need to be applied to implement the 2 surviving lessons from PR #388 analysis.

## Item 1: Add Checklist Item 7a (reviewer-rules-maintenance.md)

**File**: `.claude/agents/reviewer-rules-maintenance.md`

**Current state**: Lines 36-39 contain items 6 & 7 (4 lines total)
**Target state**: Consolidate items 6 & 7, then add new item 7a

### Replace these lines (36-39):
```
6. **Agent naming** — new agents use `reviewer-<domain>.md`
   prefix convention
7. **Orchestrator routing** — new agents must have a matching
   entry in `claude-code-review.yml` STEP 3
```

### With:
```
6. **Agent registration** — new agents must use `reviewer-<domain>.md` prefix and have a matching entry in `claude-code-review.yml` STEP 3
7. **Distributed security agents** — If the agent spec is a security auditor (permission-auditor, audit-deps, audit-hooks), verify Phase 1-2 includes inventory of legitimate plugin features (skills, hooks) BEFORE any blocking recommendations. Agents must not recommend deny rules that block their own plugin's functionality.
```

**Result**: File remains at ~49 lines (within 50-line budget)

---

## Item 2: Add Pattern 4 Section (skill-patterns.md)

**File**: `.claude/rules/skill-patterns.md`

**Current state**: File ends at line 86 with "Permission Friction Prevention" section
**Target state**: Insert new "Pattern 4: Security-Critical Agent Specs" section before "Permission Friction Prevention"

### Replace this line (76-78):
```
   - No → Ambiguous; flag as INFO for author clarification

## Permission Friction Prevention
```

### With:
```
   - No → Ambiguous; flag as INFO for author clarification

## Pattern 4: Security-Critical Agent Specs

Distributed agent specs that recommend blocking operations (deny rules,
permission restrictions) must follow a phase structure that accounts for
the plugin's own legitimate feature usage.

**Characteristics**:
- Agent is a security auditor (permission-auditor, audit-deps, audit-hooks)
- Makes recommendations about blocking/denying operations
- Phase structure: inventory → classify → recommend
- Examples: agents/permission-auditor.md, agents/audit-deps.md

**Required phases**:
1. **Inventory phase** — List legitimate protected operations from the
   plugin ecosystem (existing hooks that sandbox operations, skills that
   provide safety checks, existing deny rules already in place)
2. **Classification phase** — For each candidate operation, classify as:
   - `deny`: No protection exists, blocking is safe
   - `ask`: Legitimate uses exist but are not protected, recommend ask rules
   - `hook-protected`: Already protected by existing hooks
   - `skip`: Not a candidate for blocking
3. **Recommendation phase** — Recommend only on `deny` classified items

**Reviewer expectations**:
- Verify Phase 1 exists and inventories plugin features before recommendations
- Confirm Phase 2 uses nuanced classification, not binary yes/no decisions
- Check Phase 3 recommends only on classified `deny` items
- Flag as CRITICAL if a deny rule is recommended for an operation the plugin itself uses (paradox detection)

**Anti-pattern**: Binary "should we deny this?" logic without prior inventory
of plugin features that depend on the operation. This creates self-defeating
recommendations where the agent blocks its own ecosystem.

## Permission Friction Prevention
```

**Result**: File will be ~118 lines (well within 200-line budget)

---

## Filtered Items (Skipped)

### Item 1 (False-Positive Trap #23) — SKIPPED
**Target**: `references/review-checks-common.md`
**Reason**: Budget exceeded. File is currently 206 lines (budget: 200). Adding the trap (~5 lines) would exceed the limit to 211 lines.
**Note**: No consolidation path exists in this file to free space without removing existing false-positive traps.

### Item 3 (Severity Definition Validation) — SKIPPED
**Target**: `references/review-checks-common.md`
**Reason**: Budget exceeded. Same file as Item 1 is at 206 lines. Adding this section (~4 lines) would push to 210 lines, exceeding the 200-line budget.
