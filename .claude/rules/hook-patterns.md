# Hook Implementation Patterns

Guidance for maintaining consistent implementations when hooks exist
in multiple languages (Python and shell).

## When This Pattern Applies

When a PR adds a Python implementation of a hook that already exists
as a shell script (or vice versa), both implementations should be
functionally equivalent and use identical schemas.

Examples:
- `session_persist()` (Python) mirrors `session-stop-persist.sh`
- `session_goodbye()` (Python) mirrors `session-stop-goodbye.sh`

## Verification Checklist

### 1. Input/Output Schema Equivalence

- Both implementations read from identical stdin format (JSON)
- Both implementations write to identical stdout/file format
- Field names are identical across implementations
- Field types are compatible (JSON `true`/`false` vs shell
  `"true"`/`"false"`)

### 2. Error Handling Parity

- Both implementations handle missing stdin identically
- Both implementations handle malformed JSON identically
- Both implementations use same exit codes for error conditions
- Both implementations produce same error messages (or equivalent)

### 3. Fallback Value Consistency

- For optional fields, both implementations use identical defaults
- Missing/null values are handled the same way
- No silent failures due to different default handling

### 4. Data Type Representation

- Booleans: JSON `true`/`false` vs shell string `"true"`/`"false"`
  — aligned
- Integers: JSON `123` vs shell `"123"` — explicitly tested
- Lists: JSON array `[...]` vs shell multiline/CSV — conversion
  verified
- Timestamps: identical format (ISO8601, UTC, etc.)

### 5. Cross-Language Testing

- At least one test invokes shell implementation and parses output
- At least one test invokes Python implementation and parses output
- Both outputs are compared for schema equivalence
- Test covers at least one error condition with missing/null data

## Anti-Patterns

- Implementing Python version without testing against shell version
- Renaming fields during port (field name divergence)
- Different type representations (bool vs string) not caught by tests
- Different error handling (one throws, other returns null) — silent
  divergence
- Different fallback values in readers (one uses `""`, other uses
  `"unknown"`)

## Profile Tiers (GH-413)

Bash command validators declare a profile tier so users can dial
hook strictness up or down per session.

### Tier Assignment

| Profile | Validators | When to use |
|---------|-----------|-------------|
| `minimal` | Safety-critical rules only (DX001–DX005) | Quick fixes, throwaway scripts |
| `standard` | Minimal + skill-redirect + prefix-friction | Default for day-to-day work |
| `strict` | Standard + opinionated rules (e.g., commit-jtbd) | Feature branches, shared repos |

Each validator declares `rule_id` (stable identifier like `DX001`)
and `profile` (one of the above tiers). Lower-tier rules run at all
higher tiers — `minimal` rules are always active.

### Rule IDs

| rule_id | Validator | Tier |
|---------|-----------|------|
| DX001 | safe-subshell | minimal |
| DX002 | command-substitution | minimal |
| DX003 | execution-safety | minimal |
| DX004 | sql-safety | minimal |
| DX005 | pr-base | minimal |
| DX006 | skill-redirect | standard |
| DX007 | prefix-friction | standard |
| DX008 | commit-jtbd | strict |

### Configuration

Set via environment variables in `.claude/settings.json` or shell:

```bash
# Select profile tier (default: standard)
export DEV10X_HOOK_PROFILE=minimal

# Disable specific rules by ID (comma-separated)
export DEV10X_HOOK_DISABLE=DX006,DX008

# Enable experimental validators
export DEV10X_HOOK_EXPERIMENTAL=1
```

### Adding an Experimental Validator

New validators that need real-world validation before becoming
active-by-default should ship as `experimental=True`. Users opt
in via `DEV10X_HOOK_EXPERIMENTAL=1`. Once the validator is proven
stable, flip the flag to `False` and bump the tier appropriately.

Register the tier in `src/dev10x/validators/__init__.py`:

```python
_VALIDATOR_SPECS: list[tuple[str, str, str, str, bool]] = [
    # (module_path, class_name, rule_id, profile, experimental)
    ...
    ("dev10x.validators.new_rule", "NewRuleValidator", "DX009", "standard", True),
]
```

### Reviewer Expectations

When adding a new validator:

1. Pick a stable `rule_id` (next free `DXNNN`)
2. Choose the correct profile tier (default: `standard`)
3. Update the rule-ID table above
4. Add a unit test verifying `should_run` and `validate` behavior
5. Add an integration test covering profile filtering if the
   rule has non-trivial scope (optional)

## Reference

See `.claude/rules/hook-state-schema.md` for documenting state
schemas. See `.claude/rules/hook-input-patterns.md` for input
validation patterns.
