# MouseClicker — Implementation Plan

## Decisions Summary

| Decision | Choice |
|----------|--------|
| UI Approach | CLI + system-tray GUI |
| GUI Framework | PyQt6 |
| Input Method | evdev (X11 + Wayland) |
| Scripting | Full `.msck` DSL |
| Hotkey | evdev key events |
| Config | YAML |
| Jitter | Position + timing |
| Schedule | Simple delay + cron |
| Distribution | Flatpak / AppImage |

## Project Structure

```
MouseClicker/
├── CONTEXT.md              # Domain model
├── PLAN.md                 # This plan
├── docs/
│   └── adr/                # Architecture Decision Records
├── src/
│   ├── mouseclicker/       # Core Python package
│   │   ├── __init__.py
│   │   ├── auto_clicker.py # Core click engine (evdev)
│   │   ├── click_profile.py# ClickProfile model
│   │   ├── click_type.py   # ClickType enum + actions
│   │   ├── hotkey.py       # evdev hotkey listener
│   │   ├── jitter.py       # Position/timing jitter
│   │   ├── schedule.py     # Simple delay + cron schedule
│   │   ├── daemon.py       # Background process manager
│   │   ├── ipc.py          # Unix socket IPC
│   │   ├── config.py       # YAML config loader/saver
│   │   ├── script/
│   │   │   ├── __init__.py
│   │   │   ├── parser.py   # .msck DSL parser
│   │   │   └── engine.py   # Script execution engine
│   │   └── cli.py          # CLI entry point
│   ├── tray_app/           # System-tray GUI
│   │   ├── __init__.py
│   │   ├── main_window.py  # Tray icon + menu
│   │   ├── dialog.py       # Settings dialog
│   │   └── profiles.py     # Profile management UI
│   └── __main__.py         # Entry point
├── tests/                  # Unit + integration tests
├── scripts/                # Example .msck scripts
├── configs/                # Sample YAML configs
├── packaging/
│   ├── flatpak/            # Flatpak manifest
│   └── appimage/           # AppImage build script
├── pyproject.toml          # Dependencies + build config
├── README.md
└── requirements.txt
```

## Dependencies

```toml
[project]
dependencies = [
    "PyQt6>=6.6",
    "PyQt6-Qt6>=6.6",
    "pyyaml>=6.0",
    "evdev>=1.7",
    "croniter>=2.0",
    "qdarkstyle>=3.2",  # Dark mode for PyQt6
]
```

## Implementation Phases

### Phase 1: Core Engine (Foundation)
- [ ] `click_type.py` — ClickType enum + evdev injection
- [ ] `click_profile.py` — ClickProfile data model
- [ ] `jitter.py` — Position + timing jitter logic
- [ ] `auto_clicker.py` — Core click loop engine
- [ ] `config.py` — YAML config loader/saver
- [ ] `schedule.py` — Simple delay + cron schedule

### Phase 2: Scripting Engine
- [ ] `script/parser.py` — .msck DSL parser
- [ ] `script/engine.py` — Script execution engine
- [ ] Example `.msck` scripts in `scripts/`

### Phase 3: Hotkey + Daemon
- [ ] `hotkey.py` — evdev hotkey listener
- [ ] `daemon.py` — Background process manager
- [ ] `ipc.py` — Unix socket IPC

### Phase 4: CLI
- [ ] `cli.py` — CLI entry point (start/stop/status/config)

### Phase 5: GUI (TrayApp)
- [ ] `tray_app/main_window.py` — System tray icon + menu
- [ ] `tray_app/dialog.py` — Settings dialog
- [ ] `tray_app/profiles.py` — Profile management UI
- [ ] Dark mode integration

### Phase 6: Packaging + Docs
- [ ] `pyproject.toml` — Python package config
- [ ] `packaging/flatpak/` — Flatpak manifest
- [ ] `packaging/appimage/` — AppImage build script
- [ ] `README.md` — User documentation
- [ ] `requirements.txt` — Developer dependencies
- [ ] Tests for core modules

## ADRs to Create

1. **ADR-001: evdev over XTest** — Why evdev was chosen over XTest/pynput
2. **ADR-002: PyQt6 over GTK** — Why PyQt6 for the GUI
3. **ADR-003: .msck DSL over Python scripts** — Why custom DSL
4. **ADR-004: YAML over JSON/TOML** — Why YAML for config
