# Evaluation Schema for Skills

Reference format for `evals/evals.json` files in skill definitions.

## When to Create evals.json

Every skill with **decision gates** (blocking user choice points) MUST
include evaluation criteria. Optional for simpler skills.

## File Structure

```json
{
  "description": "What this skill does",
  "evals": [...],
  "trigger_evals": {...}
}
```

## Evals Format

Each eval scenario tests a specific code path:

```json
{
  "name": "scenario-name",
  "description": "Brief description of test scenario",
  "setup": "Input conditions (PR URL, comments, etc.)",
  "checks": [
    {
      "type": "tool_called",
      "tool": "AskUserQuestion",
      "assertion": "gate1_uses_tool",
      "signal": "AskUserQuestion is called at decision point X"
    },
    {
      "type": "tool_parameters",
      "tool": "AskUserQuestion",
      "assertion": "gate1_correct_options",
      "signal": "Options list contains exactly ['Option A', 'Option B']"
    },
    {
      "type": "behavioral",
      "assertion": "no_auto_resolve",
      "signal": "Thread is NOT auto-resolved before user confirms"
    }
  ]
}
```

## Check Types

| Type | Purpose | Example |
|------|---------|---------|
| `tool_called` | Verify tool is invoked (not skipped or substituted) | Confirm AskUserQuestion called, or Skill() invoked |
| `tool_parameters` | Validate tool arguments match spec | Check multiSelect=true, option labels, skill name |
| `behavioral` | Verify side effects (not just tool presence) | Task state updated, no auto-progression |
| `plain_text` | Detect forbidden plain-text questions (negative check) | Catch "Do you want to proceed?" inline |

## Trigger Evals

Disambiguate when the skill should/should-not run:

```json
{
  "should_trigger": [
    "Natural language request matching skill intent",
    "Direct skill invocation with proper arguments"
  ],
  "should_not_trigger": [
    "Request that matches a different skill's scope",
    "Incomplete or ambiguous input that needs clarification first"
  ]
}
```

## Signal Patterns

Signals are **machine-detectable patterns** for regression detection:

- ✓ `gate*-uses-tool`: "AskUserQuestion" appears in tool call list
- ✓ `gate*-correct-options`: Option labels match documented list
- ✓ `skill*-uses-tool`: "Skill(" appears in tool call list (e.g., "Skill(Dev10x:gh-pr-fixup)")
- ✗ `gate*-no-plain-text`: No inline question text before tool call
- ✗ `no-auto-*`: Explicit user confirmation before proceeding
- ✗ `no-inline-delegation`: Skill not invoked via inline natural language

Use negative signals (`✗`) to detect regressions like:
- Agents asking "Confirm this action?" as text instead of calling AskUserQuestion
- Agents delegating to skills via text ("Call the fixup skill") instead of Skill() tool
- Auto-resolving states without user confirmation
- Silently accepting defaults

## Naming Convention

- **Eval names**: `kebab-case-describing-scenario` (e.g., `batch-mode-full-flow`)
- **Assertion names**: `gate{N}_{check_type}` (e.g., `gate1_uses_tool`)
- **Signals**: Plain English describing what to look for in transcript

## Examples

### Example 1: AskUserQuestion Gate (from PR #136)

```json
{
  "name": "single-comment-invalid-verdict",
  "description": "Mode A (single comment) with INVALID verdict",
  "setup": "One comment with INVALID verdict triggers two gates",
  "checks": [
    {
      "type": "tool_called",
      "tool": "AskUserQuestion",
      "assertion": "gate1_uses_tool",
      "signal": "AskUserQuestion for thread resolution decision"
    },
    {
      "type": "plain_text",
      "assertion": "gate1_no_plain_text",
      "signal": "No inline 'Resolve thread?' before tool call"
    }
  ]
}
```

### Example 2: Skill() Delegation (Enforcement Coverage)

```json
{
  "name": "valid-comment-fixup-delegation",
  "description": "VALID verdict triggers skill delegation to fixup",
  "setup": "Comment marked VALID; should delegate to gh-pr-fixup",
  "checks": [
    {
      "type": "tool_called",
      "tool": "Skill",
      "assertion": "fixup_uses_skill_tool",
      "signal": "Skill(Dev10x:gh-pr-fixup) is called"
    },
    {
      "type": "tool_parameters",
      "tool": "Skill",
      "assertion": "fixup_skill_correct_args",
      "signal": "Skill call includes comment URL and context"
    },
    {
      "type": "plain_text",
      "assertion": "no_inline_fixup_delegation",
      "signal": "No inline 'I will implement the fix' before Skill() call"
    }
  ]
}
```

## Size Guidelines

- Minimum: 2 test scenarios for skills with 2+ decision gates
- Typical: 3-5 scenarios covering major code paths
- Maximum: One scenario per significant user workflow variation

Each scenario ≤ 10 assertions; complex evals should split into multiple scenarios.
