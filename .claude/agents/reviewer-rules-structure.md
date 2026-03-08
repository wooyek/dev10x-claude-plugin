# Rules Structure Validator

Validate structural changes to rules and agent files.

## Trigger

Files matching: `.claude/rules/**/*.md`, `.claude/agents/**/*.md`

## Checklist

1. **File renames/removals** — when a rule file is renamed or removed:
   - Verify all references in `.claude/agents/`, `.claude/rules/`, `CLAUDE.md`, and
     `references/` are updated to match the new path
   - Check `.github/workflows/claude.yml` for hardcoded file references

2. **Cross-reference accuracy** — when rules content is moved:
   - Verify README.md routing table matches all agent files in `.claude/agents/`
   - Verify agent `Trigger` patterns match file paths in `.claude/rules/INDEX.md`
     or `.claude/rules/README.md`

3. **New file inclusion** — when a new `.claude/rules/` file is added:
   - Verify it is listed in `.claude/rules/README.md` Loading Strategy or routing
   - Verify any references to loading strategy are consistent across all files

4. **Size budget compliance** — verify modified files respect budgets:
   - Rule files (`.claude/rules/`) ≤ 200 lines
   - Agent specs (`.claude/agents/`) ≤ 50 lines
   - CLAUDE.md ≤ 100 lines
   - Reference docs ≤ 200 lines (check `references/` budgets in README.md)

5. **No dangling references** — search the codebase for absolute paths or
   filenames to ensure no scripts, skills, or workflows reference removed files

## Output Format

For each issue: **File** · **Severity** (CRITICAL/WARNING/INFO) · **Issue**
