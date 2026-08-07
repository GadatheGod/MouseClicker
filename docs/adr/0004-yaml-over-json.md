# ADR-004: YAML over JSON/TOML

## Context

Configuration needs a human-readable, editable format. Options include YAML, JSON, or TOML.

## Decision

We chose YAML as the configuration format.

## Consequences

### Positive
- Human-readable and editable
- Supports comments (unlike JSON)
- Clean syntax for nested config
- pyyaml is well-maintained

### Negative
- Sensitive to indentation errors
- Slower parsing than JSON (negligible for config)
- Larger dependency than json module

### Mitigations
- Provide sample config files
- Validate config on load with clear error messages
- Auto-generate config if missing
