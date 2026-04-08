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

## Reference

See `.claude/rules/hook-state-schema.md` for documenting state
schemas. See `.claude/rules/hook-input-patterns.md` for input
validation patterns.
