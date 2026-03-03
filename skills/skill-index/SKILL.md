---
name: dx:skill-index
description: >
  Generate a family-grouped, adaptive-density skill index.
  Scans local skills and all installed plugins, groups by
  families.yaml, hides orchestration deps via hidden.yaml,
  and writes ~/.claude/SKILLS.md (≤45 lines, ≤300 chars/line).
user-invocable: true
invocation-name: dx:skill-index
allowed-tools:
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/skill-index/scripts/generate-motd.sh:*)
  - Read(~/.claude/SKILLS.md)
---

## Instructions

Regenerate the SKILLS.md file by running the generator script:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/skill-index/scripts/generate-motd.sh --force
```

Then display the generated file contents to the user:

```bash
cat ~/.claude/SKILLS.md
```
