# Skill Migration Design — dev10x Skills into Plugin

**Date:** 2026-02-27
**Status:** Approved

## Goal

Migrate dev10x skills from `~/.claude/skills/` into the public
`dev10x-claude-plugin` repository, sanitized of project-specific
content (secrets, workstation paths, org names, ticket IDs, emails,
Slack IDs, team UUIDs).

## Approach

Option B: Clean skills first, evaluate later.
Migrate the 6 cleanest skills as Batch 1 (one commit per skill).
After seeing the pattern in the plugin, decide which remaining skills
to include.

## Sanitization Rules

Applied to all SKILL.md files **and** scripts:

| Pattern | Replacement |
|---------|-------------|
| `janusz/PAY-xxx/...` branch | `user/TICKET-123/description` |
| `tiretutorinc/tt-pos` or similar org/repo | `your-org/your-repo` |
| `PAY-133`, `SHOP-42`, etc. | `TICKET-123` |
| Real email addresses | `user@example.com` |
| Slack user/channel/group IDs | `{YOUR_SLACK_ID}` placeholder or removed |
| `/home/janusz/` workstation paths | `~` or generic |
| `tiretutor.slack.com`, etc. | removed or generic |
| `tiretutor-team` Sentry org slug | removed or generic |
| Linear team UUIDs | removed or generic |
| `skill:audit` name | renamed to `dev10x:skill-audit` |

Scripts in `scripts/` directories are included and sanitized with
the same rules.

## Batch 1 — 6 Clean Skills (this session)

| # | Source | Plugin name | Scripts | Key sanitization |
|---|--------|-------------|---------|-----------------|
| 1 | `dev10x:tasks` | `dev10x:tasks` | None | None needed |
| 2 | `dev10x:git` | `dev10x:git` | 3 scripts | None needed in scripts; SKILL.md clean |
| 3 | `dev10x:skill-create` | `dev10x:skill-create` | None | None needed |
| 4 | `skill:audit` | `dev10x:skill-audit` | 1 script | Rename `skill:audit` → `dev10x:skill-audit` throughout |
| 5 | `dev10x:gh` | `dev10x:gh` | 4 scripts | Example output in SKILL.md + script comments |
| 6 | `dev10x:skill-motd` | `dev10x:skill-motd` | 1 script | None needed |

Each skill = one atomic git commit.

## Plugin Structure

Skills live in `skills/<namespace>:<skill-name>/SKILL.md` with
optional `scripts/` subdirectory.

```
skills/
  dev10x:tasks/
    SKILL.md
  dev10x:git/
    SKILL.md
    scripts/
      git-push-safe.sh
      git-rebase-groom.sh
      git-seq-editor.sh
  dev10x:skill-create/
    SKILL.md
  dev10x:skill-audit/
    SKILL.md
    scripts/
      extract-session.sh
  dev10x:gh/
    SKILL.md
    scripts/
      gh-pr-detect.sh
      detect-tracker.sh
      gh-issue-get.sh
      gh-issue-comments.sh
  dev10x:skill-motd/
    SKILL.md
    scripts/
      generate-motd.sh
```

## Batch 2 — To Evaluate After Batch 1

Candidates requiring moderate sanitization:

- `dev10x:todo`, `dev10x:todo-review`, `dev10x:remind`,
  `dev10x:defer`, `dev10x:wrap-up` — session workflow cluster
- `dev10x:linear` — remove team UUIDs and org URLs

## Skills to Skip

Deeply project-specific (hardcoded infrastructure, emails, IDs):
`triage-sentry`, `slack`, `k8s`, `aws-vault`, `jira`, `customer-io`,
`playwright`, `self-qa`, `gh-pr-review`, `investigate`,
`report-work-weekly`, `report-work-weekly-setup`, `jtbd`
