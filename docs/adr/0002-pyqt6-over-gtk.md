# ADR-002: PyQt6 over GTK

## Context

The GUI needs a Python framework for the system-tray application. Options include PyQt6, PyGObject (GTK), or CustomTkinter.

## Decision

We chose PyQt6 as the GUI framework.

## Consequences

### Positive
- Mature, well-documented API
- Excellent system-tray support
- Dark mode via qdarkstyle
- Professional-looking UI with minimal effort
- Large ecosystem of Qt widgets

### Negative
- Heavier dependency than GTK alternatives
- PyQt6 licensing (GPL for non-commercial use)
- Larger binary size

### Mitigations
- Use qdarkstyle for consistent dark mode
- Package with Flatpak/AppImage for easy distribution
