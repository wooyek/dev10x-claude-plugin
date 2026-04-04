# Friction Levels — Universal Enforcement Model

Three-tier enforcement model for all Dev10x skills, hooks, and
acceptance criteria. Originally defined in ADR-0002 for command
redirection; this document extends the model to cover decision
gates, acceptance criteria, and loop enforcement.

## Levels

| Level | Hook behavior | Skill gate behavior | ACC behavior |
|-------|--------------|-------------------|-------------|
| **strict** | Hard deny (exit 2) | Always block for user input | All checks run, manual gates block |
| **guided** | Hard deny + fallback | Block with recommendation, user overrides | All checks run, failures shown with guidance |
| **adaptive** | Allow + warning | Auto-select recommended option, no interruption | Auto-decide pass/fail, no AskUserQuestion |

Default: `guided` (balances enforcement with practical flexibility).

## Configuration

Friction level is set in `command-skill-map.yaml`:

```yaml
config:
  friction_level: guided  # strict | guided | adaptive
```

Per-project overrides via:
```
~/.claude/projects/<project>/memory/playbooks/skill-reinforcement.yaml
```

## Skill Decision Gates

Skills with `AskUserQuestion` gates adapt behavior based on level:

### strict

- All gates fire as documented
- No auto-selection
- User must respond to every decision point

### guided (default)

- All gates fire
- Recommended option is highlighted
- User can override or accept recommendation

### adaptive

- Gates with a `(Recommended)` option auto-select it
- No `AskUserQuestion` call — execution continues uninterrupted
- Exceptions: gates marked `ALWAYS_ASK` still fire (e.g., destructive
  operations like branch deletion, data loss scenarios)

**How to mark a gate as ALWAYS_ASK:**

```markdown
**REQUIRED: Call `AskUserQuestion`** (ALWAYS_ASK — fires at all
friction levels, including adaptive).
```

Gates without `ALWAYS_ASK` auto-resolve at adaptive level.

## Acceptance Criteria (verify-acc-dod)

| Level | Automated checks | Manual checks | Decision gate |
|-------|-----------------|---------------|---------------|
| strict | Run, must all pass | AskUserQuestion per item | AskUserQuestion required |
| guided | Run, failures shown | AskUserQuestion per item | AskUserQuestion with recommendation |
| adaptive | Run, auto-pass/fail | Converted to `prompt` (Claude evaluates) | Auto-select "Work complete" if all pass |

At adaptive level, the ACC skill runs fully unattended:
1. Execute all automated checks
2. Convert `manual` checks to `prompt` checks (Claude evaluates
   from session context)
3. If all pass → auto-complete, no user interruption
4. If any fail → queue failure report, continue with next task

## Loop Enforcement

Skills that operate in iterative loops (e.g., fix → test → fix)
must maintain skill routing on every iteration, not just the first.

| Level | Loop behavior |
|-------|--------------|
| strict | Hook blocks raw commands on every iteration |
| guided | Hook blocks + shows fallback on every iteration |
| adaptive | First iteration: skill routing enforced. Subsequent: allowed with warning logged |

The `adaptive` relaxation for loops exists because iterative
debugging sometimes requires raw commands for speed. The warning
log ensures skill-audit can detect and report deviations.

## Reading Friction Level in Skills

Skills that need friction-level awareness should read it from
the command-skill-map config. The recommended approach:

1. **Hook-based enforcement** (preferred): The PreToolUse hook
   already reads friction_level and blocks/allows accordingly.
   Most skills don't need to read it directly.

2. **Skill-level awareness** (for gate behavior): Skills that
   modify their `AskUserQuestion` behavior based on friction
   level should document the adaptive behavior in their SKILL.md
   and check session context for the level.

3. **Playbook-level override**: Playbook steps can include
   `friction_level: adaptive` to override the global setting
   for specific steps.

## Examples

### Git-groom strategy gate at adaptive level

```
Phase 2: Choose Strategy
- Friction level: adaptive
- Only fixup commits detected → auto-select "Fixup (Recommended)"
- Mixed commits detected → auto-select "Fixup (Recommended)"
- No fixups, only rewording needed → auto-select "Mass rewrite"
- Gate skipped, execution continues to Phase 3
```

### ACC at adaptive level (AFK mode)

```
Acceptance criteria (feature):

Checks:
  ✅ Working copy clean
  ✅ CI passing
  ✅ PR not draft
  ✅ No fixup commits
  ✅ Loop compliance (auto-evaluated: all test runs via skill)
  ✅ PR ready (solo maintainer)

6/6 checks passed. Auto-completing — adaptive mode.
```

## Migration Path

Skills adopting friction-level awareness should:

1. Document adaptive behavior in SKILL.md (what auto-selects)
2. Mark destructive gates as `ALWAYS_ASK`
3. Add tests for adaptive auto-selection logic
4. Update playbook steps if level-specific behavior differs

## References

- ADR-0002: Data-driven skill redirect with friction levels
- `src/dev10x/validators/command-skill-map.yaml`: Config source
- `src/dev10x/validators/skill_redirect.py`: Hook implementation
- `skills/verify-acc-dod/SKILL.md`: First skill-level adopter
