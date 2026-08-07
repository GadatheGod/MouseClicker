# ADR-003: .msck DSL over Python scripts

## Context

Users need a way to write automation scripts. Options include a custom DSL (.msck), raw Python scripts, or both.

## Decision

We chose a custom `.msck` DSL as the primary scripting format.

## Consequences

### Positive
- Simple syntax for common automation tasks
- No Python knowledge required
- Consistent behavior across Python versions
- Easy to version control and share

### Negative
- Requires a custom parser
- Less powerful than Python for complex logic
- Must maintain the DSL specification

### Mitigations
- Support Python scripts as an advanced option in the future
- Document DSL thoroughly with examples
- Keep the DSL simple and intuitive
