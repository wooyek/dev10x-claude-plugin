# Changelog

All notable changes to the Dev10x Claude Code Plugin are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

## 0.27.0 — Self-Healing Code Review

Released 2026-03-15

The shipping pipeline now fixes its own review findings autonomously.
Also: GitHub Issues support in project-scope and auto-approval for safe
subshell commands.

### Features

- **Self-healing code review** — work-on shipping pipeline now dispatches
  `dev10x:review` + `dev10x:review-fix` to autonomously create fixup commits
  for review findings ([GH-252])
- **Full task visibility in unattended mode** — git-commit and gh-pr-create
  create all startup tasks regardless of mode; auto-skipped tasks are
  immediately marked completed with reason ([GH-251])
- **GitHub Issues in project-scope** — Phase 3 Tracker Dispatch now supports
  GitHub Issues alongside Linear and JIRA, with batch creation pattern for
  10+ issues ([GH-244])
- **Auto-approval for safe subshells** — new `HookAllow` result type lets
  read-only subshell commands like `basename "$(git rev-parse ...)"` pass
  without permission prompts ([GH-247])
- **Worktree permission merging** — merge allow rules accumulated in worktree
  sessions back into the main project settings
- **Batch plugin permission updates** — auto-detect latest plugin version
  and update stale versioned paths across all projects in one pass

### Bug Fixes

- Prevent path errors when CWD drifts during session ([GH-251])

## 0.26.0 — Release Notes as a Skill

Released 2026-03-15

Track what you ship with playbook-powered release notes — configurable
ticket patterns, output targets (stdout/GitHub/Slack), and release/hotfix
plays.

### Features

- **Release notes skill** — generic, playbook-powered release notes generation
  with configurable ticket patterns, output targets (stdout/GitHub/Slack),
  and release/hotfix plays

## 0.25.0 — Unattended Shipping

Released 2026-03-15

Skills can now commit, format, and ship without human intervention.
Playbook fragments eliminate duplication, unattended git-commit bypasses
all interactive gates, and ruff formatting runs automatically on every
Python edit.

### Features

- **Reusable playbook fragments** — extract shared step sequences (like the
  9-step shipping pipeline) into named fragments, reducing duplication from
  36 of 55 steps across 4 plays ([GH-232])
- **Unattended git-commit** — when invoked by an orchestrating skill with
  an active task list, all interactive gates are bypassed: auto-stage,
  auto-select commit type, auto-generate problem/solution ([GH-237])
- **Automated ruff formatting** — PostToolUse hook runs `ruff format` +
  `ruff check --fix` on every Python file edit ([GH-231])
- **Post-response shipping continuation** — gh-pr-respond now offers to
  groom, push, and monitor CI after fixup commits ([GH-225])
- **Redundant command detection** — hook blocks `git -C <path>` when CWD
  already matches, and `cd <cwd> && ...` noop chains ([GH-225])
- **Respond playbook comment hiding** — gh-pr-respond can hide obsolete
  review comments after addressing them ([GH-226])
- **uv-managed test execution** — pyproject.toml with pytest/ruff dev deps
  so `uv run pytest` works without extra flags ([GH-225])

### Bug Fixes

- **Skill-audit enforcement gaps** — AskUserQuestion rule extended to global
  scope, Linear API fallback for non-autolinked prefixes ([GH-227])
- Ensure release script stages pyproject.toml after bump

## 0.24.0 — Auto-Advance Pipeline

Released 2026-03-14

The shipping pipeline no longer blocks on preview approval. Commits and
draft PR creation proceed automatically with a code-reviewer agent step.

### Features

- **Auto-advance shipping pipeline** — commits and draft PR creation proceed
  without blocking on preview approval, with code-reviewer agent step ([GH-213])
- Community link added to README

## 0.23.0 — Domain-Driven Design Workshops

Released 2026-03-12

Explore and model domain architecture with Event Storming directly from
Claude Code sessions.

### Features

- **DDD workshop skill** — bootstrap Domain-Driven Design Event Storming
  workshops for domain exploration and modeling ([GH-219])

### Bug Fixes

- Declare missing `allowed-tools` in 6 skills to eliminate per-invocation
  approval prompts ([GH-70])

## 0.22.0 — Playbook Architecture

Released 2026-03-12

The biggest architectural release to date. Work plans become reusable,
customizable playbooks. The hook dispatcher consolidates 7 processes into
one with ~80% overhead reduction. User-space config overrides ship.

### Features

- **Playbook architecture** — generalize work plans into reusable,
  customizable playbooks with convention-based discovery. Any orchestration
  skill can become playbook-powered by adding `references/playbook.yaml`.
  User overrides stored per-skill in memory ([GH-209])
- **Guided work plan customization** — dedicated `dev10x:work-plan` skill
  with list, view, edit, and reset subcommands ([GH-209])
- **Per-project work plan customization** — projects can override plan
  templates without modifying plugin source ([GH-140])
- **Consolidated hook dispatcher** — replace 7 separate hook processes
  with one unified Python dispatcher using a validator registry.
  ~80-85% hook overhead reduction ([GH-208])
- **User-space config overrides** — `~/.claude/skill-index/` for
  `families.yaml` and `hidden.yaml` without modifying plugin source ([GH-10])
- **Alias enforcement** — block raw `git` commands with env-var prefixes
  or `$(git merge-base ...)` subshells when aliases exist ([GH-200])
- **Automated issue closing** — GitHub Actions workflow parses `Fixes:` URLs
  from merged PR bodies and closes referenced issues ([GH-209])

### Refactoring

- Split reviewer-skill into structure and behavior specs
- Trim CLAUDE.md to stay within 100-line budget
- Prefer jq and yq over manual JSON/YAML parsing ([GH-196])

## 0.21.0 — One-Command Review Requests

Released 2026-03-11

Assign GitHub reviewers and notify Slack in a single skill invocation.
PR creation now works in repos without a develop branch.

### Features

- **Combined review request skill** — `dev10x:request-review` assigns
  GitHub reviewers and posts Slack notification in one command ([GH-188])
- **PR creation without develop** — gh-pr-create works in repos that
  use main as their only branch ([GH-180])
- **Prevent WIP in worktrees** — new worktrees no longer inherit
  uncommitted changes from the parent branch
- **Dynamic base branch validation** — hook validates PR target branch
  at creation time ([GH-187])

### Bug Fixes

- Prevent silent project linkage failures in Linear ([GH-153])

## 0.20.0 — Reliable Skill Orchestration

Released 2026-03-09

Numbered lists replace code blocks across 39 skills so decision gates and
orchestration steps actually fire instead of being skipped as examples.

### Features

- **Bundled call spec pattern** — complex tool call specifications live
  in `tool-calls/` sidecar files, referenced from SKILL.md enforcement
  markers ([GH-179])
- **Numbered list enforcement** — 39 skills updated to use numbered lists
  (not code blocks) for mandatory TaskCreate/AskUserQuestion calls ([GH-179])
- Centralize rules documentation into INDEX.md

## 0.19.0 — MCP Tools & Project Scoping

Released 2026-03-08

Native MCP server tools replace fragile Bash wrappers. Multi-ticket
projects get first-class scoping with Linear, JIRA, and GitHub Issues.
Dozens of enforcement fixes improve skill reliability.

### Features

- **MCP tools** — GitHub, Git, and Database operations exposed as MCP
  server tools, replacing fragile Bash-based wrappers ([GH-126])
- **Project-scope skill** — scaffold multi-ticket projects with milestones,
  blocking relationships, and tracker integration. Supports Linear, JIRA,
  and GitHub Issues ([GH-154])
- **Skill eval criteria** — measurable quality gates for skill behavior,
  enabling automated detection of decision gate violations ([GH-133])
- **Auto-resolved PR reviewers** — GitHub team reviewers resolved
  automatically from CODEOWNERS ([GH-118])
- **Temp file MCP tool** — `mktmp` tool prevents temp file collisions
  across concurrent sessions ([GH-143])
- **Upstream issue filing from audits** — skill-audit findings can be
  filed as GitHub issues at the plugin repo ([GH-135])
- **Parallel subagent dispatch** — skill-audit runs analysis phases
  concurrently ([GH-131])
- **Pre-approved tool access** — 17 skills declare `allowed-tools`
  to eliminate per-invocation approval prompts ([GH-70])

### Bug Fixes

- Enforce AskUserQuestion at all decision gates ([GH-133], [GH-151])
- Enforce TaskCreate orchestration at startup ([GH-134])
- Prevent Write tool error in commit workflow ([GH-126])
- Prevent GIT_SEQUENCE_EDITOR permission friction ([GH-121])
- Exclude .claude/worktrees/ from hook copies ([GH-144])
- Allow bare fixup commits from humans ([GH-159])

## 0.18.0 — Documentation

Released 2026-03-07

Updated README with installation instructions.

## 0.17.0 — Task Orchestration Everywhere

Released 2026-03-07

Every skill now tracks progress with structured tasks. Orchestration
patterns (auto-advance, batched decisions, tier-based complexity)
retrofitted across the entire skill catalog.

### Features

- **Task orchestration framework** — define patterns for task tracking,
  auto-advance, batched decisions, and tier-based complexity across all
  skills
- **Mandatory task tracking** — every skill now creates startup tasks
  and updates them as phases complete
- Retrofit orchestration into 4 flagship skills, Tier Full, Tier Standard,
  and PR lifecycle skills

## 0.16.0 — Documentation

Released 2026-03-06

Document external tool dependencies in README.

## 0.15.0 — Cross-Platform Skills

Released 2026-03-06

Skills now work in OpenAI Codex alongside Claude Code via a compatible
skill pack and install tooling.

### Features

- **Codex-compatible skill pack** — install tooling for OpenAI Codex
  environments alongside Claude Code
- Fix local type and test discovery for mirrored skills

### Self-Improving Review System

- Clarify PR title gitmoji mapping and JTBD third-party variants
- Clarify self-motivated work conventions

## 0.14.0 — The Great Consolidation

Released 2026-03-05

11 sub-plugins merged into one unified Dev10x plugin with a consistent
`dev10x:` namespace and cross-script compatible directory resolution.

### Refactoring

- **Single plugin consolidation** — merge 11 separate plugin directories
  into one unified Dev10x plugin with consistent `dev10x:` namespace
- Refactor directory resolution for cross-script compatibility
- Remove unused session-start-git-aliases hook
- Clarify hook-blocked and advisory patterns in session guidance

## 0.13.0 — Convention Polish

Released 2026-03-04

Surface @mentions at start of Slack review messages and establish
conventions for agent directories and skill naming.

### Refactoring

- Surface @mentions at start of Slack review messages
- Establish conventions for agent directories and skill naming

## 0.12.0 — Namespace Unification

Released 2026-03-04

Every skill gets the `dev10x:` prefix. Skills are isolated into 11
domain-specific sub-plugins with distributed hooks and marketplace
discovery.

### Refactoring

- **Namespace unification** — standardize all skill invocation names
  from mixed `dx:`, `ticket:`, `pr:`, `qa:` prefixes to `dev10x:`
- **Multi-plugin architecture** — isolate skills into 11 domain-specific
  sub-plugins (fundamentals, git, gh, db, tickets, sessions, parking,
  py, skills, slack, qa) with distributed hooks
- Enable marketplace to discover all sub-plugins

## 0.11.0 — Permission Auditing

Released 2026-03-04

Systematically audit Claude Code permission settings for security gaps.
Config-driven Slack notifications and dual-format skill index also ship.

### Features

- **Permission security auditing** — systematic audit agent for
  Claude Code permission settings
- **Config-driven Slack notifications** — per-project Slack channel
  and mention configuration for review requests
- **Dual-format skill index** — MOTD and SKILLS.md output formats
  with proper `dev10x:` invocation prefixes
- Use Haiku model in GitHub Actions for faster CI

### Refactoring

- Delegate Slack and reviewer steps from pr-monitor to dedicated skills
- Stabilize test suite with proper dependencies

## 0.10.0 — Database Access & Session Guidance

Released 2026-03-03

Safe database querying with SQL validation hooks and intelligent
session-start recommendations. Family-grouped skill index and acceptance
criteria verification round out the release.

### Features

- **Database querying** — safe, customizable database access via plugin
  with SQL validation hooks
- **Family-grouped skill index** — adaptive-density display with YAML
  config for families and hidden skills
- **Acceptance criteria verification** — work-on checks criteria before
  shipping ([GH-86])
- **Session guidance** — surface wrapper discovery and git alias
  recommendations at session start ([GH-87])
- **Slack review readability** — improved formatting ([GH-54])
- Preserve plugin permissions across upgrades ([GH-79])

### Bug Fixes

- Detect `postgresql://` scheme in SQL safety hook
- Detect `psql` in chained commands
- Stabilize mktmp.sh and groom script paths

## 0.9.0 — Release Stability

Released 2026-03-02

Prevent version number skipping in releases.

### Bug Fixes

- Prevent version number skipping in releases

## 0.6.0 — Ticket Management & QA Automation

Released 2026-03-02

Full ticket lifecycle from branch creation to technical scoping. QA test
execution as a portable plugin skill. Context-aware rule loading reduces
always-loaded token overhead.

### Features

- **Ticket management suite** — branch creation, ticket creation, JTBD
  story write-back, and technical scoping for Linear tickets
- **QA automation** — portable plugin skills for QA test execution
- **ADR creation** — Architecture Decision Records as a plugin skill
- **Context-aware rule loading** — reduce always-loaded rules by scoping
  them to relevant file patterns ([GH-68])
- **Obsolete review summary hiding** — automatically hide stale PR review
  summaries in interactive and CI modes ([GH-44])
- **User task injection** — inject tasks during work-on execution ([GH-59])
- **Temp file collision prevention** — namespace-based temp files ([GH-19])
- **Workspace-agnostic Slack** — notifications work from any directory
- **Reusable technical scoping** — base scoping workflow for tickets and ADRs

### Bug Fixes

- Prevent review workflow self-cancellation

## 0.4.0 — Cleanup

Released 2026-03-02

Remove obsolete docs plans.

## 0.2.0 — Genesis

Released 2026-03-02

Initial release with 40+ skills covering the full development lifecycle
in a single plugin.

### Features

- **Plugin scaffold** — manifest, marketplace installation, semver releases
- **Session management** — task tracking, skill-usage audit, session wrap-up,
  MOTD with available skills
- **Work orchestration** — task-list-driven `work-on` skill with acceptance
  criteria verification
- **Git workflow** — safe rebase/force-push with branch protection, structured
  commits, atomic commit splitting, branch history grooming, retroactive
  ticket tracking, scoped fixup commits, git alias detection
- **PR lifecycle** — automated PR creation with JTBD stories, autonomous
  monitoring, review requests, comment response orchestration, comment
  triage/validation, session bookmarking, inline review findings, fixup
  commits from review comments
- **Parking/deferral** — code-level deferrals, smart routing, Slack DM
  reminders, cross-source discovery
- **JTBD drafting** — reusable Job Story generation for consistent business
  narratives
- **Worktrees** — isolated worktrees with IDE-safe branch separation,
  dual-mode creation
- **Linear integration** — MCP operations reference without tool duplication
- **Skill authoring** — creation without permission friction, templates,
  JTBD guidance
- **Plugin-distributed hooks** — safety and quality hooks shipped with
  the plugin
- **Self-executing Python** — UV-based script execution ([GH-17])
- **Self-improving review system** — lessons from PR reviews automatically
  strengthen review checks

---

[GH-1]: https://github.com/WooYek/Dev10x/issues/1
[GH-7]: https://github.com/WooYek/Dev10x/issues/7
[GH-10]: https://github.com/WooYek/Dev10x/issues/10
[GH-15]: https://github.com/WooYek/Dev10x/issues/15
[GH-17]: https://github.com/WooYek/Dev10x/issues/17
[GH-19]: https://github.com/WooYek/Dev10x/issues/19
[GH-31]: https://github.com/WooYek/Dev10x/issues/31
[GH-33]: https://github.com/WooYek/Dev10x/issues/33
[GH-35]: https://github.com/WooYek/Dev10x/issues/35
[GH-44]: https://github.com/WooYek/Dev10x/issues/44
[GH-45]: https://github.com/WooYek/Dev10x/issues/45
[GH-50]: https://github.com/WooYek/Dev10x/issues/50
[GH-54]: https://github.com/WooYek/Dev10x/issues/54
[GH-59]: https://github.com/WooYek/Dev10x/issues/59
[GH-68]: https://github.com/WooYek/Dev10x/issues/68
[GH-70]: https://github.com/WooYek/Dev10x/issues/70
[GH-79]: https://github.com/WooYek/Dev10x/issues/79
[GH-84]: https://github.com/WooYek/Dev10x/issues/84
[GH-86]: https://github.com/WooYek/Dev10x/issues/86
[GH-87]: https://github.com/WooYek/Dev10x/issues/87
[GH-118]: https://github.com/WooYek/Dev10x/issues/118
[GH-121]: https://github.com/WooYek/Dev10x/issues/121
[GH-126]: https://github.com/WooYek/Dev10x/issues/126
[GH-131]: https://github.com/WooYek/Dev10x/issues/131
[GH-133]: https://github.com/WooYek/Dev10x/issues/133
[GH-134]: https://github.com/WooYek/Dev10x/issues/134
[GH-135]: https://github.com/WooYek/Dev10x/issues/135
[GH-140]: https://github.com/WooYek/Dev10x/issues/140
[GH-143]: https://github.com/WooYek/Dev10x/issues/143
[GH-144]: https://github.com/WooYek/Dev10x/issues/144
[GH-151]: https://github.com/WooYek/Dev10x/issues/151
[GH-153]: https://github.com/WooYek/Dev10x/issues/153
[GH-154]: https://github.com/WooYek/Dev10x/issues/154
[GH-157]: https://github.com/WooYek/Dev10x/issues/157
[GH-159]: https://github.com/WooYek/Dev10x/issues/159
[GH-179]: https://github.com/WooYek/Dev10x/issues/179
[GH-180]: https://github.com/WooYek/Dev10x/issues/180
[GH-187]: https://github.com/WooYek/Dev10x/issues/187
[GH-188]: https://github.com/WooYek/Dev10x/issues/188
[GH-196]: https://github.com/WooYek/Dev10x/issues/196
[GH-200]: https://github.com/WooYek/Dev10x/issues/200
[GH-208]: https://github.com/WooYek/Dev10x/issues/208
[GH-209]: https://github.com/WooYek/Dev10x/issues/209
[GH-213]: https://github.com/WooYek/Dev10x/issues/213
[GH-219]: https://github.com/WooYek/Dev10x/issues/219
[GH-225]: https://github.com/WooYek/Dev10x/issues/225
[GH-226]: https://github.com/WooYek/Dev10x/issues/226
[GH-227]: https://github.com/WooYek/Dev10x/issues/227
[GH-231]: https://github.com/WooYek/Dev10x/issues/231
[GH-232]: https://github.com/WooYek/Dev10x/issues/232
[GH-237]: https://github.com/WooYek/Dev10x/issues/237
[GH-244]: https://github.com/WooYek/Dev10x/issues/244
[GH-247]: https://github.com/WooYek/Dev10x/issues/247
[GH-251]: https://github.com/WooYek/Dev10x/issues/251
[GH-252]: https://github.com/WooYek/Dev10x/issues/252
