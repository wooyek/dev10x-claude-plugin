---
name: dev10x:skill-motd
description: >
  Generate the Skills Reference MOTD shown at session start.
  Scans all skills, extracts metadata, and writes a pre-rendered
  ~/.claude/SKILLS.md grouped by category.
user-invocable: true
invocation-name: skill-motd
---

## Instructions

Regenerate the SKILLS.md file by running the generator script:

```bash
~/.claude/skills/dev10x:skill-motd/scripts/generate-motd.sh --force
```

Then display the generated file contents to the user:

```bash
cat ~/.claude/SKILLS.md
```
