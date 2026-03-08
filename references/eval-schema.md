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
| `tool_called` | Verify tool is invoked (not skipped or substituted) | Confirm AskUserQuestion is called |
| `tool_parameters` | Validate tool arguments match spec | Check multiSelect=true, option labels |
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
- ✗ `gate*-no-plain-text`: No inline question text before tool call
- ✗ `no-auto-*`: Explicit user confirmation before proceeding

Use negative signals (`✗`) to detect regressions like:
- Agents asking "Confirm this action?" as text instead of calling AskUserQuestion
- Auto-resolving states without user confirmation
- Silently accepting defaults

## Naming Convention

- **Eval names**: `kebab-case-describing-scenario` (e.g., `batch-mode-full-flow`)
- **Assertion names**: `gate{N}_{check_type}` (e.g., `gate1_uses_tool`)
- **Signals**: Plain English describing what to look for in transcript

## Example from PR #136

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

## Decision Gate Coverage

When a skill has N documented decision gates (marked `REQUIRED: Call AskUserQuestion`):

1. Count the gates in SKILL.md (search for "REQUIRED: Call AskUserQuestion")
2. Verify evals.json includes assertions for ALL N gates
3. If a gate is branch-conditional (e.g., gate 1 only on free-text input),
   create a separate eval scenario that triggers that branch

Example: skill with 3 gates
- Scenario A: Triggers gates 2, 3 (via ticket reference input)
- Scenario B: Triggers gates 1, 2, 3 (via free-text input)
- Result: All 3 gates have explicit assertions

## Size Guidelines

- Minimum: 2 test scenarios for skills with 2+ decision gates
- Typical: 3-5 scenarios covering major code paths
- Maximum: One scenario per significant user workflow variation

Each scenario ≤ 10 assertions; complex evals should split into multiple scenarios.
