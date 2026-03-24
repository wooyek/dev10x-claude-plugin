# Lessons Learned: PR #136 Analysis

**Repository**: Brave-Labs/dev10x-ai
**PR Number**: 136
**Title**: 🐛 GH-133 Enforce AskUserQuestion at decision gates
**Author**: wooyek
**Status**: Merged
**Analysis Date**: 2026-03-08

---

## Executive Summary

PR #136 addresses a critical compliance gap: **decision gates in skills were documented with soft guidance, but agents were substituting plain text questions instead of calling the `AskUserQuestion` tool**. This undermines structured decision-making because plain text questions:

1. Don't block execution
2. Don't provide clickable options for the user
3. Break the orchestration contract defined in `references/task-orchestration.md`

The PR introduces **three key improvements**:
1. **Explicit enforcement markers** in skill documentation (`REQUIRED: Call AskUserQuestion`)
2. **Comprehensive evaluation criteria** with measurable assertions
3. **Compliance check** in the skill-audit tool to detect plain-text regressions

---

## Statistics

| Metric | Value |
|--------|-------|
| Files Changed | 3 |
| Lines Added | 267 |
| Lines Deleted | 4 |
| Skill Files Modified | 2 |
| New Evals Created | 3 test scenarios |
| Decision Gates Enforced | 4 |
| Eval Dimensions Defined | 4 |

---

## Changes Analysis

### 1. **skills/gh-pr-respond/SKILL.md**

**Change Type**: Enhancement with enforcement markers
**Lines Added**: 29 | **Lines Deleted**: 4

#### What Changed

- **New section** (lines 40-58): "Decision Gates" explicitly lists 4 blocking points with mandatory enforcement markers
- **Replaced soft guidance** with `REQUIRED: Call AskUserQuestion` at each decision point:
  - Line 130: Mode A, Step 1b (thread resolution confirmation)
  - Line 158: Mode A, Step 3 (continue/batch/stop offer)
  - Line 232: Mode B, Step 3 (batch approval)
  - Line 289: Mode B, Step 5 (thread resolution confirmation)

#### Key Language Improvements

**Before:**
```
Use `AskUserQuestion` with options:
```

**After:**
```
**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
This blocks execution until the user responds. Options:
```

This shift from soft guidance to enforcement markers solves the problem where agents would ask the question as plain text (which doesn't block) then optionally call the tool.

#### Why This Matters

The decision gates are **blocking points** — the skill's design assumes execution pauses until the user makes a choice. Plain text questions allow agents to proceed without waiting, silently accepting a default or allowing auto-progression. This fundamentally breaks the skill's orchestration contract.

---

### 2. **skills/gh-pr-respond/evals/evals.json** (New File)

**Change Type**: New evaluation criteria
**Lines Added**: 229

This is a comprehensive evaluation framework with 4 dimensions and 3 test scenarios. **This is the most important contribution** — it shows exactly what "correct" looks like and how to detect regressions.

#### Eval Dimensions

1. **Decision Gate Compliance** — All 4 gates use `AskUserQuestion` tool calls, never plain text
2. **Option Correctness** — Each gate presents the documented options with correct labels and multiSelect values
3. **No Auto-Resolve** — Threads are never auto-resolved; resolution requires explicit user confirmation
4. **Task Orchestration** — TaskCreate/TaskUpdate calls track progress correctly per mode

#### Test Scenarios

**Eval 1: single-comment-invalid-verdict**
- Tests Mode A (single comment) with INVALID verdict
- Validates Gate 1 (thread resolution) and Gate 2 (continue/batch/stop)
- Includes 5 specific assertions with "signals" for detection:
  - ✓ `gate1-uses-tool`: AskUserQuestion is called for thread resolution
  - ✓ `gate1-no-plain-text`: No inline "Resolve this thread?" before tool call
  - ✓ `gate1-correct-options`: Exactly 2 options (Resolve, Leave open)
  - ✓ `gate2-uses-tool`: AskUserQuestion for continue/batch/stop
  - ✓ `gate2-correct-options`: Exactly 3 options (Next comment, Switch to batch, Stop)
  - ✓ `no-auto-resolve-on-invalid`: Thread is NOT auto-resolved

**Eval 2: batch-mode-full-flow**
- Tests Mode B (batch) with 4 comments (2 VALID, 2 INVALID)
- Validates Gate 3 (batch approval) and Gate 4 (thread resolution)
- 8 assertions including behavioral checks:
  - ✓ Gate 3 doesn't ask as plain text "Approve all, or specify?"
  - ✓ Gate 4 appears AFTER all replies are posted
  - ✓ No threads resolved before user confirms via Gate 4
  - ✓ Task tracking for batch mode

**Eval 3: single-comment-valid-no-remaining**
- Edge case: VALID verdict, no remaining comments
- Validates that gates are **skipped appropriately** (not all gates fire every time)
- Tests delegation to `Dev10x:gh-pr-fixup`

#### Trigger Evals (Coverage)

The `trigger_evals` section defines when the skill **should** and **should NOT** trigger:

**Should Trigger:**
- Direct invocation with PR URL (batch)
- Direct invocation with specific comment (single)
- Natural language requests ("help me respond to these comments")
- Review-scoped batch requests
- PR number only

**Should NOT Trigger:**
- Review creation requests (that's `Dev10x:gh-pr-review`)
- Direct fixup requests (that's `Dev10x:gh-pr-fixup`)
- Monitoring queries (that's `Dev10x:gh-pr-monitor`)
- Thread resolution requests (not the full triage workflow)
- Triage-only requests (that's `Dev10x:gh-pr-triage`)

---

### 3. **skills/skill-audit/SKILL.md**

**Change Type**: Compliance check addition
**Lines Added**: 9

Added AskUserQuestion enforcement check to Phase 3 (Compliance Check):

```markdown
**AskUserQuestion enforcement check:** When a SKILL.md documents
`AskUserQuestion` (or marks a step as `REQUIRED: AskUserQuestion`),
verify the session transcript contains an actual `AskUserQuestion`
tool call at that decision point — not a plain text question. If
the transcript shows the agent asked the question as inline text
instead of calling the tool, classify it as:
- **DEVIATED** with assessment **regression** — plain text
  questions don't block execution and lack structured options
```

This creates a **feedback loop**: the skill-audit tool can now detect when agents violate the AskUserQuestion constraint and flag them as regressions, which feeds back into memory and SKILL.md updates.

---

## Review Feedback Analysis

**Review Comments**: None recorded
**Review Rounds**: 1
**Merge Status**: Merged without blocking feedback

### Observations

The PR merged without recorded reviewer feedback, which suggests:
1. The changes are straightforward enough to be self-evident
2. The enforcement markers are unambiguous and needed
3. No controversy about marking decision gates as mandatory

However, the **absence of feedback is itself instructive**:
- The `evals.json` file is 229 lines of highly specific assertions
- No reviewer questioned the assertion format or added/removed dimensions
- This indicates **evaluations are new to the codebase** and may not have established review patterns yet

---

## Identified Improvements by Domain

### A. CLAUDE.md & Documentation

#### High Priority

1. **Document "Decision Gates" pattern as a reusable convention** (CLAUDE.md)
   - Location: Add new subsection under "Skill Naming Convention" or "Code Review"
   - Content: Define when a step is a "blocking decision gate" and the enforcement markers
   - Rationale: PR #136 establishes `REQUIRED: AskUserQuestion` as a pattern; this should be systematized so future skills adopt it consistently
   - Action: Add 3-4 lines to CLAUDE.md documenting the pattern

2. **Clarify "plain text questions" anti-pattern** (CLAUDE.md or essentials.md)
   - Problem: The PR solves the problem without documenting why plain text is unacceptable
   - Content: "Soft guidance ('Use AskUserQuestion') allows agents to substitute plain text. Plain text questions don't block, lack options, and break orchestration. All decision gates MUST use tool calls."
   - Location: `.claude/rules/essentials.md` under "Orchestration" section
   - Rationale: This gives future Claude instances context for why the enforcement exists

#### Medium Priority

3. **Add "Decision Gates" section template to CLAUDE.md**
   - Provide a copy-paste template for skills with decision gates
   - Include the table format from gh-pr-respond/SKILL.md lines 49-54
   - Rationale: Reduces friction for future skills that need gate enforcement

---

### B. Agent Specs (`.claude/agents/`)

#### High Priority

1. **Update reviewer-skill.md with Decision Gate checklist**
   - Add to "Behavioral constraint language" section (line 94) or new subsection
   - New checklist item:
     ```
     **Decision gates enforcement** — When a PR adds/modifies a skill's
     documented decision point (marked `REQUIRED: AskUserQuestion` or
     `REQUIRED: Call ...`):
     (a) Verify the enforcement marker is present in SKILL.md
     (b) Check that evals/evals.json includes assertions to detect
         regressions (plain text substitution)
     (c) Verify skill-audit Phase 3 can detect violations
     Do NOT merge PRs that document decision gates without enforcement markers.
     ```
   - Rationale: Prevents future PRs from reverting to soft guidance

2. **Add evaluation dimension review pattern**
   - When `evals/evals.json` is created/modified, review for:
     - ✓ 3+ test scenarios covering major code paths
     - ✓ Assertions include "signals" (patterns that should/should not appear)
     - ✓ Trigger evals differentiate should/should-not cases
   - Rationale: Ensures evals.json stays high-quality and maintainable

---

### C. Rules Files (`.claude/rules/`)

#### High Priority

1. **Create or expand `.claude/rules/skill-gates.md`** (New file)
   - Define the "Decision Gate" pattern:
     - What triggers a gate (user choice point that affects execution)
     - When to use `AskUserQuestion` vs other decision methods
     - Enforcement marker syntax (`REQUIRED: ...`)
     - How to write assertions for evals.json
   - Size: ~80-100 lines
   - Rationale: Makes the pattern explicit so it's discoverable and consistent across skills
   - Link from: CLAUDE.md, essentials.md, reviewer-skill.md

2. **Update `.claude/rules/essentials.md`**
   - Add subsection "Decision Gates and Orchestration"
   - Content:
     ```
     ## Decision Gates and Orchestration

     Skills with blocking decision points MUST use `AskUserQuestion` tool calls,
     never plain text questions. This ensures:
     - Execution blocks until the user responds (not auto-progressed)
     - Options are clickable and structured (not free-text)
     - The skill's documented flow is respected (not silently altered)

     Mark every decision gate in SKILL.md with:
     **REQUIRED: Call `AskUserQuestion`** (do NOT use plain text)

     See `.claude/rules/skill-gates.md` for the full pattern.
     ```
   - Rationale: Essentials loads in every session; this makes the constraint visible upfront

---

### D. Skill Design

#### High Priority

1. **Extract eval assertions into a shared schema** (Potential refactor)
   - Current issue: `evals.json` has inline schema for "check" types (tool_called, behavioral, tool_parameters, etc.)
   - Opportunity: Define a JSON schema or TypeScript types for `evals.json` so tooling can validate/standardize
   - Rationale: As more skills adopt evals.json, standardized schema prevents drift
   - Action: Create `scripts/eval-schema.json` or `references/eval-schema.md`
   - Impact: Future evals can self-validate; reviewers have clear expectations

2. **Add skill-audit detection for missing evals** (skill-audit.md Phase 2)
   - Current: skill-audit detects MISSED skill invocations
   - Opportunity: Also detect when a skill SHOULD have evals but doesn't
   - Rule: If a SKILL.md documents `AskUserQuestion` or other decision gates but has no `evals/evals.json`, flag as GAP
   - Rationale: Ensures compliance mechanisms are in place (not just documented)

#### Medium Priority

3. **Define "minimal evals" baseline for new skills**
   - Recommendation: Every skill with 2+ decision gates should have ≥2 test scenarios
   - Recommendation: Every skill with user-modifiable behavior should have trigger evals (should/should-not)
   - Rationale: Prevents skills from shipping without testability

---

### E. Orchestrator & Automation

#### Medium Priority

1. **Update Claude Code Review Orchestrator** (if `claude-code-review.yml` exists)
   - Trigger: When files matching `skills/**/evals/evals.json` are changed
   - Route to: `reviewer-skill.md` (already correct)
   - Add context: Evaluations are critical for decision-gate compliance
   - Rationale: Ensures evals.json diffs are reviewed as carefully as SKILL.md changes

2. **Consider skill-audit as pre-merge check**
   - Opportunity: Add a GitHub Actions workflow that runs skill-audit on merged PRs to detect regressions in production
   - Rationale: Catches cases where agents violate documented constraints even after code review
   - Impact: Feedback loop improves CLAUDE.md and skill definitions

---

## Action Items

### High Priority (Implement Soon)

| # | Action | Owner | File | Estimated Impact |
|---|--------|-------|------|------------------|
| 1 | Document "Decision Gates" pattern in CLAUDE.md | Dev10x | CLAUDE.md | High — Prevents future soft-guidance issues |
| 2 | Add Decision Gate checklist to reviewer-skill.md | Dev10x | .claude/agents/reviewer-skill.md | High — Prevents regression to soft guidance |
| 3 | Create `.claude/rules/skill-gates.md` | Dev10x | .claude/rules/skill-gates.md (new) | High — Establishes reusable pattern |
| 4 | Clarify "plain text questions" anti-pattern | Dev10x | .claude/rules/essentials.md | Medium — Educational, improves consistency |

### Medium Priority (Implement in Next Review Cycle)

| # | Action | Owner | File | Estimated Impact |
|---|--------|-------|------|------------------|
| 5 | Update reviewer-skill.md evaluation dimension checklist | Dev10x | .claude/agents/reviewer-skill.md | Medium — Standardizes eval review |
| 6 | Add skill-audit Phase 2 detection for missing evals | Dev10x | skills/skill-audit/SKILL.md | Medium — Ensures compliance mechanisms exist |
| 7 | Define minimal evals baseline for new skills | Dev10x | CLAUDE.md | Low-Medium — Guidance for future skills |
| 8 | Extract eval assertions into shared schema | Dev10x | references/eval-schema.md (new) | Low — Future-proofs eval.json |

### Low Priority (Discussion/Exploration)

| # | Action | Owner | Notes |
|---|--------|-------|-------|
| 9 | Consider skill-audit as GitHub Actions pre-merge check | Dev10x | Would require CI setup; good long-term investment |
| 10 | Evaluate trigger-evals pattern applicability | Dev10x | PR #136 introduces this in 1 skill; should we standardize? |

---

## Patterns & Insights

### Pattern 1: "Soft Guidance" vs "Enforcement"

**The Problem**:
- Documentation says "Use AskUserQuestion"
- But agents substitute plain text (which isn't wrong, just weaker)
- No mechanism detects the deviation

**The Solution (from PR #136)**:
- Mark decision gates with `REQUIRED: Call AskUserQuestion`
- Include assertions in evals.json that explicitly check for tool usage
- Add skill-audit detection for plain-text substitution

**Lesson for Future Work**:
Any constraint that relies on agent self-discipline (without enforcement) will gradually erode. Use:
1. **Documentation markers** (REQUIRED: ...)
2. **Evaluation assertions** (evals.json with specific checks)
3. **Automated detection** (skill-audit Phase 3 compliance)

### Pattern 2: Specification via Evaluation

**Insight**: The evals.json file is actually a **specification** — it defines what "correct" looks like more precisely than prose alone.

Example from PR #136:
- Prose: "Use AskUserQuestion with options..."
- Evals assertion: "Gate 1 AskUserQuestion has exactly 2 options: 'Resolve' and 'Leave open'"

The assertion is more precise and testable than any README description could be.

**Lesson**: For complex behaviors, consider writing evals before writing the skill implementation. Evals force clarity about requirements.

### Pattern 3: Edge Cases via Trigger Evals

**Insight**: The `trigger_evals.should_not_trigger` section is as important as `should_trigger`.

Example from evals.json:
- ✓ Should trigger: "review this PR and leave comments" → NO, that's Dev10x:gh-pr-review
- ✓ Should NOT trigger: "review this PR and leave comments"

This disambiguates overlapping intents and prevents the skill from mishandling adjacent workflows.

**Lesson**: When defining a skill's scope, explicitly list what it should NOT do. This prevents scope creep and clarifies boundaries.

---

## False Positives & Risk Mitigation

### Potential Risk: Over-Enforcement

**Risk**: Requiring `AskUserQuestion` at every decision point could be overkill for minor choices (e.g., "Do you want to continue? (y/n)")

**Mitigation from PR #136**:
- Decision gates are **explicitly listed** (4 gates, not arbitrary)
- Each gate has documented **purpose** (confirm action, get approval, collect decisions)
- The pattern is NOT applied to every question — only blocking gates

**Recommendation**: In future implementations, differentiate:
- **Decision Gates** (blocking, affect execution flow) → Use AskUserQuestion
- **Information Questions** (clarifications) → Can use plain text

---

### Potential Risk: Evaluation Maintenance Burden

**Risk**: Creating evals.json adds complexity; future maintainers may not update it when the skill changes.

**Mitigation**:
- skill-audit Phase 3 can flag evals that are outdated
- Reviewer checklist should verify evals are updated in the same PR as SKILL.md changes
- Over time, standard assertion patterns will emerge (reducing authoring burden)

**Recommendation**: Document evaluation maintenance as part of skill development lifecycle.

---

## Summary of Improvements for Review Process

### What This PR Does Well

1. ✅ **Explicit enforcement markers** — Removes ambiguity about whether a tool call is optional
2. ✅ **Comprehensive evaluation criteria** — Specifies exactly what correct behavior looks like
3. ✅ **Backwards feedback loop** — skill-audit can now detect and report regressions
4. ✅ **Edge case coverage** — Evals include scenarios where gates are skipped appropriately
5. ✅ **Trigger disambiguation** — Evals clarify when the skill should/should-not run

### What Could Be Improved Going Forward

1. ⚠️ **Pattern documentation** — The "Decision Gates" pattern should be formalized in CLAUDE.md or essentials.md
2. ⚠️ **Agent reviewer updates** — reviewer-skill.md should have a checklist for decision gate enforcement
3. ⚠️ **Evaluation schema** — As more skills adopt evals.json, a standardized schema would help
4. ⚠️ **Skill-audit Phase 2** — skill-audit should detect missing evals (not just missing tool calls)

---

## Recommendations

### For Code Review Process

1. **Always require evals.json for skills with decision gates**
   - Rationale: Evals make requirements testable and prevent future regressions
   - Implementation: Add checklist item to reviewer-skill.md

2. **Update reviewer-skill.md with behavioral constraint language**
   - Rationale: Ensures future PRs don't revert to soft guidance
   - Implementation: Add item #19 to the checklist

3. **Document Decision Gates pattern in essentials.md**
   - Rationale: Makes the pattern visible in every session
   - Implementation: Add ~4 lines under "Orchestration" section

### For Skill Development

1. **Adopt "specification via evaluation" for complex skills**
   - Rationale: Evals force clarity about expected behavior
   - Implementation: Encourage authors to write evals.json early in development

2. **Use trigger_evals to disambiguate skill boundaries**
   - Rationale: Prevents scope creep and confusion with adjacent skills
   - Implementation: Example in gh-pr-respond shows the pattern; make it standard

3. **Differentiate Decision Gates from information questions**
   - Rationale: Prevents over-use of AskUserQuestion for trivial clarifications
   - Implementation: Document in skill-gates.md (proposed above)

---

## Conclusion

PR #136 successfully closes a compliance gap where agents were substituting plain text questions for tool calls. The solution — enforcement markers + comprehensive evaluations + automated detection — creates a virtuous cycle:

1. **Documentation** is explicit (REQUIRED: ...)
2. **Evaluation** is precise (evals.json with assertions)
3. **Detection** is automated (skill-audit Phase 3)
4. **Feedback** improves future SKILL.md definitions

The main opportunity for improvement is to **propagate this pattern** across the review process and codebase so it becomes a standard practice rather than a one-off fix.

**Key metrics**:
- **Pattern established**: Yes (Decision Gates + REQUIRED markers)
- **Evaluation framework created**: Yes (evals.json with 3 test scenarios)
- **Compliance mechanism added**: Yes (skill-audit Phase 3)
- **Documentation updated**: Partial (CLAUDE.md and essentials.md could be enhanced)
- **Review process updated**: No (reviewer-skill.md should be updated)

**Overall quality**: High. This PR addresses a real problem with a systematic solution that creates foundation for similar improvements in the future.
