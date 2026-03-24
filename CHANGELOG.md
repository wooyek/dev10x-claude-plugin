# Changelog

All notable changes to the Dev10x Claude Code Plugin are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

## 0.37.0 — Skill Compliance Enforcement

Released 2026-03-24

Agents can no longer bypass skill delegations or use raw CLI
commands where skills exist. A new PreToolUse hook auto-denies
known CLI anti-patterns, SKILL.md enforcement markers prevent
inline handling of sub-skill operations, and a new MCP tool
eliminates the permission friction that incentivized bypasses.

### Features

- **Auto-deny wrong-tool drift** — PreToolUse hook blocks raw
  CLI commands (git commit -m, gh pr create, git push) that
  should go through skill wrappers, while allowing skill-internal
  patterns like -F and --fixup ([GH-397])
- **Frictionless PR comment replies** — new `pr_comment_reply`
  MCP tool replaces raw `gh api` calls in gh-pr-fixup,
  gh-pr-respond, and gh-pr-triage, removing per-invocation
  Bash permission prompts ([GH-399])

### Improvements

- **Sub-skill delegation enforcement** — gh-pr-respond gains
  REQUIRED: Skill() markers at all 5 delegation points (triage,
  fixup, groom, push, monitor), plus branch location pre-check
  and stash guard in git-groom ([GH-400])
- **Review delegation bypass prevention** — gh-pr-respond adds
  negative instruction prohibiting manual fixes; skill-reinforcement
  gains workflow-context checking for delegation bypasses ([GH-401])
- **Audit-driven skill hardening** — gh-pr-respond, gh-pr-fixup,
  and git-fixup gain mandatory markers for parallel dispatch,
  test gates, and CWD pre-checks based on audit findings ([GH-407])
- **Eval schema for Skill() assertions** — evaluation schema
  documents Skill() invocation assertion patterns, enabling
  detection of enforcement bypass regressions ([b90c5de])

[GH-397]: https://github.com/wooyek/dev10x-ai/issues/397
[GH-399]: https://github.com/wooyek/dev10x-ai/issues/399
[GH-400]: https://github.com/wooyek/dev10x-ai/issues/400
[GH-401]: https://github.com/wooyek/dev10x-ai/issues/401
[GH-407]: https://github.com/wooyek/dev10x-ai/issues/407
[b90c5de]: https://github.com/wooyek/dev10x-ai/commit/b90c5de

## 0.36.0 — PR Monitor Visibility & MCP Bugfix

Released 2026-03-23

PR monitoring reports full status context, and the MCP
pr_comments tool resolves a parameter mapping bug that
blocked all comment operations.

### Features

- **PR monitor status reporting** — monitor agent surfaces
  CI check details, unhandled review comments, and reviewer
  assignment status instead of completing silently ([GH-392])

### Bug Fixes

- **pr_comments parameter mapping** — fix `--pr-number` to
  `--pr` in cli_server.py so reply, resolve, and thread
  operations work correctly ([GH-393])

[GH-392]: https://github.com/wooyek/dev10x-ai/issues/392
[GH-393]: https://github.com/wooyek/dev10x-ai/issues/393

## 0.35.0 — Orchestration Integrity & Maintenance Skills

Released 2026-03-22

Skill delegation is enforced end-to-end, new maintenance skills
catch memory rot and playbook drift before they cause failures,
and CI deduplication eliminates wasted review runs.

### Features

- **Memory health auditing** — new `Dev10x:memory-maintenance`
  skill detects stale paths, script-calling instructions,
  contradictions, and MEMORY.md index drift ([GH-375])
- **Playbook drift detection** — new `Dev10x:playbook-maintenance`
  skill compares user overrides against defaults, surfacing new
  steps and prompt changes with severity levels ([GH-366])
- **Skill-usage reinforcement** — orchestration skill identifies
  CLI commands that should be replaced by dedicated skills or MCP
  tools, with prefix-matched command-to-skill mapping ([GH-384])
- **Project settings cleanup** — permission-maintenance gains
  Step 6 to strip duplicate, wildcard-covered, and stale rules
  from project settings files ([GH-386])
- **CI SHA deduplication** — GitHub Actions workflows skip
  redundant runs when a peer workflow already handles the same
  commit SHA ([GH-382])

### Improvements

- **Skill delegation enforcement** — work-on requires post-step
  Skill() verification and prohibits pipeline collapse during
  fanout execution ([GH-367])
- **CI re-monitoring after force push** — git-groom and work-on
  mandate `Dev10x:gh-pr-monitor` after any force push to avoid
  stale CI results ([GH-371])
- **Task reconciliation after delegation** — work-on reconciles
  parent task state after child skill completion, preventing
  orphaned tasks ([GH-376])
- **Wrong-database prevention** — db-psql requires target database
  comment prefix on manual SQL and sets PGAPPNAME for process
  identification ([GH-363])
- **Scope-aware fanout parsing** — fanout distinguishes scope URLs
  from specific item URLs, restricting scans to matching commands
  ([GH-351])
- **Skill routing through compaction** — compaction preservation
  directive keeps routing tables intact across context compression
  ([GH-358])
- **Unmatched play fallback** — work-on routes unmatched plays to
  the feature play instead of failing, and bans merge operations
  in gh-pr-monitor ([GH-357])
- **CWD-based worktree detection** — ticket-branch detects
  worktree context from current working directory ([GH-353])
- **Auto-filing audit findings** — skill-audit findings file
  automatically as GitHub issues ([GH-356])
- **Nested-mode task exemption** — formalized exemption for
  TaskCreate in nested skill invocations ([GH-355])

### Bug Fixes

- **Auditor deny-rule overreach** — permission-auditor now uses
  three-tier classification (deny/ask/hook-protected/skip) instead
  of blanket deny recommendations that blocked legitimate skills
  ([GH-385])
- **Premature completion gate** — work-on completion gate no longer
  fires before all tasks are finished ([GH-354])
- **Explore agent source failures** — GitHub/JIRA fetch subagents
  switched from Explore to general-purpose to gain Bash access
  ([GH-348])

## 0.34.0 — Fanout Safety & Skill Consistency

Released 2026-03-21

Fanout delegation is hardened against bypass and wrong-branch
commits, and trigger/skip documentation is standardized across
all skills.

### Bug Fixes

- **Fanout delegation safety** — prevent delegation bypass and
  wrong-branch commits with stricter orchestration guards
  ([GH-345])

### Improvements

- **Trigger/skip standardization** — consistent trigger and skip
  documentation across all skills, completing the effort started
  in v0.33.0 ([GH-313])

## 0.33.0 — Orchestration Discipline & Session Resilience

Released 2026-03-21

Fanout enforces structured work-on delegation, session state
survives compaction and restarts, and acceptance criteria
verification becomes a reusable skill.

### Features

- **Session resilience** — pre-compaction hook preserves critical
  context, session state persists across restarts, and skill
  invocation metrics are tracked for audit ([GH-310]–[GH-317])
- **Fanout orchestration discipline** — work-on delegation is now
  REQUIRED with enforcement language, per-issue subtask tracking,
  and new Monitor + Audit phases ([GH-338], [GH-339])
- **Full shipping pipeline in gh-pr-respond** — post-response
  continuation expanded from groom+push+monitor to the complete
  groom → push → ready → monitor → merge lifecycle with
  solo-maintainer auto-merge support ([GH-338], [GH-339])
- **Reusable definition-of-done verification** — extracted
  `Dev10x:verify-acc-dod` skill for consistent acceptance checks
  across work-on, fanout, and future orchestrators ([GH-340])

### Improvements

- **Task tracking in DDD and permission-maintenance** — both skills
  gain TaskCreate/TaskUpdate orchestration for supervisor visibility
  ([GH-41])
- **Statusline enrichment** — branch name and worktree context shown
  in terminal statusline ([GH-312])
- **Skill scaffolding** — `Dev10x:skill-create` generates directory
  structure with scripts via `scaffold.sh` ([GH-314])
- **Plugin health verification** — install and verify scripts validate
  plugin structure after updates ([GH-315])
- **Marketplace metadata** — enriched `marketplace.json` for better
  plugin discovery ([GH-317])
- **Trigger/skip standardization** — consistent trigger and skip
  documentation across 13+ skills ([GH-313])

## 0.32.0 — Permission Friction & Review Hardening

Released 2026-03-20

Permission friction eliminated across skill-audit, project-scope, and
py-uv skills. Code review agents gain stricter verification checks,
and work-on enforces playbook verification before plan generation.

### Features

- **Playbook verification in work-on** — Phase 3 now requires reading
  and verifying a playbook file before generating tasks, preventing
  ad-hoc plan generation that skips configured steps ([GH-308])
- **GitHub async timing checks** — code review agents detect stale
  `gh pr checks` results after force-pushes by verifying check count
  against expected baselines ([GH-318])
- **Table/implementation skew detection** — code review agents flag
  documentation tables that diverge from actual implementation

### Improvements

- **Reduced permission friction** — normalized `scripts/:*` to
  `scripts/*:*` across all `allowed-tools` declarations in skill-audit,
  py-uv, skill-create, and codex-skills equivalents ([GH-321])
- **Smarter sensitive file hook** — `block-sensitive-file-write.py` now
  uses basename matching instead of substring, eliminating false
  positives on sidecar metadata files like `.vars` ([GH-322])
- **Project-scope anti-patterns** — documented command substitution and
  env var prefix friction patterns to avoid in `gh` commands, switched
  sidecar files from `.env` to `.vars` ([GH-322])
- **Autosquash alias prefix** — `env` command prefix added to
  `GIT_SEQUENCE_EDITOR=true` in autosquash aliases for consistent
  shell expansion ([GH-319])
- **Skill name normalization** — Dev10x skill names normalized across
  documentation and scripts for consistency
- **Semicolon false positive fix** — SQL safety hook no longer blocks
  semicolons inside string literals like `STRING_AGG(name, '; ')`
  ([GH-320])

### Bug Fixes

- **Skill-audit permission prompt** — `extract-session.sh` no longer
  triggers approval prompts on every invocation due to mismatched
  `allowed-tools` glob pattern ([GH-321])

### Documentation

- **Updated skill pattern references** — all `scripts/:*` documentation
  examples updated to `scripts/*:*` across skill-audit, skill-create,
  and their codex-skills equivalents ([GH-309])

## 0.31.0 — MCP Consolidation & Parallel Workflows

Released 2026-03-20

MCP servers consolidate from 4 to 2, PR creation runs through native
MCP tools, macOS Keychain credentials land, and work-on gains parallel
stream processing with context compaction.

### Features

- **MCP tools for PR creation** — 6 gh-pr-create scripts and pr-notify
  wrapped as 7 MCP tools in gh_server.py, enabling dual-path transition
  with existing Bash paths ([GH-191])
- **Universal branch aliases** — git log, diff, rebase, and autosquash
  aliases now support main and master alongside existing develop,
  development, and trunk variants ([GH-288])
- **Non-destructive CTE in db queries** — db hook allows WITH clauses
  that don't modify data, unblocking analytical queries ([GH-303])
- **Slack thread investigation** — new plugin skill investigates Slack
  bug reports, root-causes in codebase, and creates Linear tickets
  ([#298])
- **Guided Slack integration setup** — interactive skill walks through
  Slack app creation, token configuration, and channel setup ([GH-14])
- **macOS Keychain credential retrieval** — secrets can be stored and
  retrieved via macOS Keychain as an alternative to env vars ([GH-119])

### Improvements

- **MCP server consolidation** — reduced from 4 servers to 2 (cli →
  git + utils, gh stays), cutting startup overhead ([GH-194])
- **Parallel work stream processing** — work-on dispatches independent
  tasks concurrently instead of sequentially ([#301])
- **Context compaction in orchestration** — skills compact context at
  phase boundaries to stay within token limits ([#299])
- **Work-on audit enforcement** — audit findings from GH-295, GH-296,
  GH-297 enforced as playbook and eval updates ([#300])
- **False positive prevention** — shared code patterns (MCP imports,
  PEP 723 inlining) no longer trigger review warnings ([#294])
- **Broader permission maintenance** — permission update workflow
  covers more path patterns and project configurations
- **Playbook pattern documentation** — reviewer guidance for validating
  playbook-powered skills and reference file patterns ([#243])
- **External tool declaration requirements** — skill authors must
  declare all external tool dependencies in SKILL.md front matter
  ([#270])
- **Invocation-name enforcement** — reviewer checklist enforces
  mandatory invocation-name field with exact-match rule ([#267])

### Testing

- **Automated hook testing** — pytest CI pipeline validates hook
  scripts with unit tests ([GH-214])
- **CI concurrency groups** — prevent duplicate CI runs on rapid
  pushes to the same branch ([GH-214])

### Bug Fixes

- **Non-interactive autosquash** — autosquash aliases wrap
  GIT_SEQUENCE_EDITOR=true to avoid escaping issues that broke alias
  expansion ([GH-288])

## 0.30.0 — Disciplined Orchestration

Released 2026-03-19

Work-on orchestration gets guardrails — mechanical plan generation,
mandatory phase tasks, and supervisor sign-off prevent shortcuts.
Git-domain skills gain MCP tool access, session skills get aligned
names, and script-path leaks are eliminated across the tooling surface.

### Features

- **MCP tool access for git skills** — git-domain skills can call MCP
  tools directly instead of shelling out via Bash wrappers ([GH-192])
- **Permission management skill** — base permission management enables
  structured allow/deny rule handling ([GH-274])
- **Slack file cleanup** — cleanup Slack config files and prompt for
  missing configuration ([GH-271])
- **Goodbye message** — session exit shows a resume command so users can
  pick up where they left off ([GH-272])
- **Block `$(cat ...)` substitution** — hook blocks command substitution
  via `cat` to prevent file content leaks in shell commands ([GH-277])

### Improvements

- **Aligned session skill names** — 11 session skills get consistent
  `Dev10x:` prefixed invocation names ([GH-224], [GH-102])
- **Script-path leak elimination** — skill tooling no longer leaks
  resolved cache paths in allowed-tools or Bash calls ([GH-280],
  [GH-275], [GH-283])
- **Destructive git commands ADR** — documented the decision to block
  destructive git operations by default ([GH-269])
- **Orchestration guardrail evals** — eval assertions enforce Phase 3
  mechanical planning and supervisor sign-off ([GH-248], [GH-273])

### Bug Fixes

- **Supervisor sign-off required** — plan completion gate now requires
  explicit supervisor confirmation instead of auto-completing ([GH-273])
- **Natural language plan mapping** — phrases like "show me the plan"
  route to AskUserQuestion gate, not plan mode ([GH-248])
- **Mechanical Phase 3** — plan generation enforces 1:1 task-to-step
  mapping from playbook, preventing step collapsing ([GH-248], [GH-273])
- **Phase task verification** — Phase 2 blocked until all 4 phase tasks
  are confirmed to exist ([GH-248])
- **ExitPlanMode prohibition** — work-on sessions cannot use Claude
  Code's built-in plan mode, preserving task tracking ([GH-248])
- **MCP-aware subagent routing** — Phase 2 fetches requiring MCP tools
  (Linear, Slack, Sentry) route to general-purpose agents, not Explore
  agents which lack MCP access ([GH-155])

## 0.29.0 — Smoother Shipping

Released 2026-03-16

Worktrees handle Husky v4 and Yarn Berry correctly, fish shell stops
breaking GraphQL queries, and delegated skills skip redundant task
tracking for faster unattended execution.

### Improvements

- **Unattended PR creation** — gh-pr-create supports `--unattended` flag
  with documented detection conditions and gate bypass rules ([GH-263])
- **Delegated skills skip TaskCreate** — skills invoked as subtasks of a
  parent orchestrator skip internal task tracking, reducing noise ([GH-258])
- **Body-only review handling** — gh-pr-respond Mode B handles reviews with
  body text but no inline comments, common from CI bots ([GH-258])
- **Non-skippable monitor output** — gh-pr-monitor Step 4 marked as
  non-skippable so users always see background agent progress ([GH-259])
- **Reduced work-on friction** — workspace detection extracted to script,
  implicit plan approval when user provides a complete plan ([GH-253])
- **Friction-free grooming** — raw GIT_SEQUENCE_EDITOR rebase replaced with
  git autosquash-develop alias to avoid env-prefix permission friction ([GH-253])

### Bug Fixes

- **Husky v4 and Yarn Berry in worktrees** — detect Husky version, bootstrap
  ~/.huskyrc for v4, use version-aware yarn install flags ([GH-222])
- **Fish shell GraphQL compatibility** — convert GraphQL examples to
  double-quoted with escaped `$` to prevent fish interpolation ([GH-258])

## 0.28.0 — Conflict-Free PRs

Released 2026-03-16

PRs now auto-detect and resolve merge conflicts before they reach reviewers.
MCP servers start reliably, and jq queries no longer trigger false-positive
obfuscation blocks.

### Improvements

- **Conflict-free PRs** — PR creation and monitoring detect merge conflicts
  via `git merge-tree` and GitHub's mergeable API, with auto-rebase +
  force-with-lease resolution ([GH-261])
- **Consistent skill naming** — 9 skills get proper `Dev10x:` invocation
  names with documented branding rationale ([GH-234])
- **Friction-free issue status checks** — jq concatenation pattern replaces
  interpolation to avoid obfuscation detection ([GH-260])
- **Full changelog** — all 22 releases (v0.2.0–v0.27.0) documented with
  themed headlines and linked issue references
- **MCP server permission review checks** — reviewer-infra now explicitly
  requires `+x` on server scripts

### Bug Fixes

- **MCP server startup** — 3 server scripts (db, gh, git) were missing
  execute permissions, causing "Permission denied" on startup

## 0.27.0 — Self-Healing Code Review

Released 2026-03-15

The shipping pipeline now fixes its own review findings autonomously.
Also: GitHub Issues support in project-scope and auto-approval for safe
subshell commands.

### Features

- **Self-healing code review** — work-on shipping pipeline now dispatches
  `Dev10x:review` + `Dev10x:review-fix` to autonomously create fixup commits
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
- **Guided work plan customization** — dedicated `Dev10x:work-plan` skill
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

- **Combined review request skill** — `Dev10x:request-review` assigns
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
`Dev10x:` namespace and cross-script compatible directory resolution.

### Refactoring

- **Single plugin consolidation** — merge 11 separate plugin directories
  into one unified Dev10x plugin with consistent `Dev10x:` namespace
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

Every skill gets the `Dev10x:` prefix. Skills are isolated into 11
domain-specific sub-plugins with distributed hooks and marketplace
discovery.

### Refactoring

- **Namespace unification** — standardize all skill invocation names
  from mixed `dx:`, `ticket:`, `pr:`, `qa:` prefixes to `Dev10x:`
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
  with proper `Dev10x:` invocation prefixes
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
[GH-253]: https://github.com/WooYek/Dev10x/issues/253
[GH-258]: https://github.com/WooYek/Dev10x/issues/258
[GH-259]: https://github.com/WooYek/Dev10x/issues/259
[GH-260]: https://github.com/WooYek/Dev10x/issues/260
[GH-261]: https://github.com/WooYek/Dev10x/issues/261
[GH-263]: https://github.com/WooYek/Dev10x/issues/263
[GH-267]: https://github.com/WooYek/Dev10x/issues/267
[GH-269]: https://github.com/WooYek/Dev10x/issues/269
[GH-270]: https://github.com/WooYek/Dev10x/issues/270
[GH-271]: https://github.com/WooYek/Dev10x/issues/271
[GH-272]: https://github.com/WooYek/Dev10x/issues/272
[GH-273]: https://github.com/WooYek/Dev10x/issues/273
[GH-274]: https://github.com/WooYek/Dev10x/issues/274
[GH-275]: https://github.com/WooYek/Dev10x/issues/275
[GH-277]: https://github.com/WooYek/Dev10x/issues/277
[GH-280]: https://github.com/WooYek/Dev10x/issues/280
[GH-283]: https://github.com/WooYek/Dev10x/issues/283
[GH-288]: https://github.com/WooYek/Dev10x/issues/288
[GH-313]: https://github.com/WooYek/Dev10x/issues/313
[GH-345]: https://github.com/WooYek/Dev10x/issues/345
[GH-348]: https://github.com/WooYek/Dev10x/issues/348
[GH-351]: https://github.com/WooYek/Dev10x/issues/351
[GH-353]: https://github.com/WooYek/Dev10x/issues/353
[GH-354]: https://github.com/WooYek/Dev10x/issues/354
[GH-355]: https://github.com/WooYek/Dev10x/issues/355
[GH-356]: https://github.com/WooYek/Dev10x/issues/356
[GH-357]: https://github.com/WooYek/Dev10x/issues/357
[GH-358]: https://github.com/WooYek/Dev10x/issues/358
[GH-363]: https://github.com/WooYek/Dev10x/issues/363
[GH-366]: https://github.com/WooYek/Dev10x/issues/366
[GH-367]: https://github.com/WooYek/Dev10x/issues/367
[GH-371]: https://github.com/WooYek/Dev10x/issues/371
[GH-375]: https://github.com/WooYek/Dev10x/issues/375
[GH-376]: https://github.com/WooYek/Dev10x/issues/376
[GH-382]: https://github.com/WooYek/Dev10x/issues/382
[GH-384]: https://github.com/WooYek/Dev10x/issues/384
[GH-385]: https://github.com/WooYek/Dev10x/issues/385
[GH-386]: https://github.com/WooYek/Dev10x/issues/386
[#243]: https://github.com/WooYek/Dev10x/pull/243
[#267]: https://github.com/WooYek/Dev10x/pull/267
[#270]: https://github.com/WooYek/Dev10x/pull/270
