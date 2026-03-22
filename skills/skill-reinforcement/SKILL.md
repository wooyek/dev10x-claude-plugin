---
name: Dev10x:skill-reinforcement
description: >
  Remind the agent about available skills when it uses CLI commands
  that should be handled by skills or MCP tools instead. Reads
  conversation context to identify the offending command, matches
  it against a command-to-skill map, and outputs a firm reinforcement
  message pointing to the correct skill.
  TRIGGER when: user sees agent using CLI instead of a skill, user
  rejects a command that should have been a skill, or user says
  "use the skills".
  DO NOT TRIGGER when: agent is already using skills correctly,
  or the CLI command has no skill equivalent.
user-invocable: true
invocation-name: Dev10x:skill-reinforcement
allowed-tools:
  - Read(~/.claude/SKILLS.md)
  - Read(${CLAUDE_PLUGIN_ROOT}/skills/skill-reinforcement/references/*)
---

# Dev10x:skill-reinforcement

Quick reinforcement nudge when an agent reaches for CLI commands
instead of using available skills or MCP tools.

## When to Use

Invoke this skill when:
- The agent ran a CLI command that a skill already handles
- You rejected a command and want the agent to use a skill instead
- You approved a command but want to reinforce the skill habit
- You want to say "use the skills" with a structured response

## Orchestration

**REQUIRED: Create a task at invocation.** Execute at startup:

1. `TaskCreate(subject="Reinforce skill usage", activeForm="Reinforcing")`

Mark completed when done: `TaskUpdate(taskId, status="completed")`

## Instructions

### Step 1: Identify the offending command

Scan the recent conversation for the CLI command that triggered
this invocation. Look for:
- The most recent `Bash` tool call that was rejected or approved
- Any command the user flagged as wrong
- If the user provided arguments (e.g., `/Dev10x:skill-reinforcement kubectl`),
  use that as the command identifier

Store the command string for matching.

### Step 2: Match against command-skill map

Read the command-skill mapping from
`${CLAUDE_PLUGIN_ROOT}/skills/skill-reinforcement/references/command-skill-map.yaml`.

Match the identified command against the `patterns` list in each
mapping entry. Use prefix matching — if the command starts with
any pattern in the list, it matches that entry.

If no match is found in the map, fall back to Step 3.

### Step 3: Fall back to SKILLS.md

If no direct mapping exists, read `~/.claude/SKILLS.md` and scan
skill descriptions from the system-reminder context to find the
best match based on the command's purpose.

### Step 4: Output reinforcement message

Output a firm, concise reinforcement message with these sections:

1. **Command detected:** — the CLI command that was identified
2. **Use instead:** — skill invocation name and one-line description
3. **Why:** — reason from the map entry (if available)
4. **How to invoke:** — `Skill("<skill-name>")` call syntax
5. **Related skills:** — from the map entry (if available)

If multiple skills could apply, list all of them ranked by
relevance.

### Step 5: Reinforce the general principle

End with a brief reminder:

> Always check if a skill or MCP tool exists before reaching for
> CLI commands. Skills provide consistent behavior, proper tool
> declarations, and avoid permission friction.

## Examples

### Example 1: kubectl usage

**User:** `/Dev10x:skill-reinforcement`
(after agent ran `kubectl get pods -n staging`)

**Output:**
```
## Skill Reinforcement

**Command detected:** `kubectl get pods -n staging`
**Use instead:** `/Dev10x:k8s` — Kubernetes operations via
aws-vault authenticated kubectl

**Why:** Direct kubectl calls bypass aws-vault authentication
and may fail or use wrong credentials.

**How to invoke:**
Skill("Dev10x:k8s")
```

### Example 2: direct git push

**User:** `/Dev10x:skill-reinforcement`
(after agent ran `git push origin feature-branch`)

**Output:**
```
## Skill Reinforcement

**Command detected:** `git push origin feature-branch`
**Use instead:** `/Dev10x:git` — Safe git push with
protected branch checks

**Why:** Direct git push bypasses force-push protection
on develop/main branches.

**How to invoke:**
Skill("Dev10x:git")
```

### Example 3: no match found

**User:** `/Dev10x:skill-reinforcement`
(after agent ran `curl https://api.example.com/health`)

**Output:**
```
## Skill Reinforcement

**Command detected:** `curl https://api.example.com/health`
**No direct skill match found.**

Available skills that might help:
- `/Dev10x:k8s` — if checking service health in k8s
- `/Dev10x:investigate` — if investigating a bug report

Check ~/.claude/SKILLS.md for the full list of available skills.
```
