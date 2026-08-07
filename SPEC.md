# MouseClicker — Product Requirements Document (PRD)

## Problem Statement

Linux users who need a mouse auto-clicker (gamers, automation enthusiasts, data entry workers) have limited options. The most popular existing tool, MouseClickTool, is Windows-only (C#/WPF). Linux users must either use Windows VMs with the tool, rely on command-line utilities like `xdotool` (which lack GUI and scripting), or juggle multiple tools for auto-clicking, hotkeys, and scheduling. There is no single, polished, cross-desktop auto-clicker for Linux that supports modern features like Wayland, custom scripting, and system-tray management.

## Solution

Build MouseClicker — a complete mouse auto-clicker for Linux that runs on both X11 and Wayland. The tool provides:

1. A **Daemon** that executes click profiles and scripts via `evdev`
2. A **TrayApp** (system-tray GUI) for visual control
3. A **CLI** for headless/automated usage
4. A **custom DSL** (`.msck` files) for writing automation scripts
5. **Multiple click profiles** with save/switch capability
6. **Scheduled triggers** (simple delay or cron-based)
7. **Random jitter** (position + timing) to avoid detection
8. **Global hotkeys** for toggling start/stop

The tool is distributed as a Flatpak or AppImage, with an optional systemd service for daemon mode.

## User Stories

1. As a gamer, I want to set up a left-click auto-clicker with a configurable interval, so that I can automate repetitive clicking in games without holding down the mouse button
2. As a power user, I want to create multiple click profiles (e.g., "gaming", "data entry", "scrolling"), so that I can quickly switch between different click configurations
3. As a user on Wayland, I want the auto-clicker to work reliably without depending on X11, so that I can use it on modern Ubuntu, Fedora, and Arch installations
4. As a casual user, I want a system-tray GUI with a simple start/stop button, so that I can control the auto-clicker without opening a terminal
5. As a gamer, I want random position and timing jitter applied to my clicks, so that games don't detect my auto-clicker as a bot
6. As a power user, I want to set a global hotkey (e.g., Ctrl+Alt+A) to toggle the auto-clicker on/off, so that I can quickly start and stop without using the GUI
7. As a data entry worker, I want to write automation scripts using a simple DSL, so that I can automate complex sequences of clicks, scrolls, and program launches
8. As a sysadmin, I want to run the auto-clicker as a systemd service, so that it runs in the background on a headless server without a display
9. As a user, I want the tool to save my configuration between sessions, so that I don't have to reconfigure it after a reboot
10. As a power user, I want to schedule the auto-clicker to start at a specific time using a cron expression, so that I can automate tasks overnight
11. As a casual user, I want to schedule the auto-clicker to start after a simple delay (e.g., "start in 5 minutes"), so that I can set it and walk away
12. As a user, I want to use the CLI to start/stop the auto-clicker, so that I can control it from scripts or terminal sessions
13. As a gamer, I want to perform long-press clicks (press, hold for N seconds, release), so that I can simulate holding down the mouse button for drag-and-drop operations
14. As a user, I want to scroll the mouse wheel programmatically, so that I can automate scrolling in web pages or documents
15. As a power user, I want to launch external programs from a script, so that I can automate workflows that involve opening applications
16. As a user, I want the GUI to support dark mode, so that it matches my desktop environment's appearance
17. As a user, I want to specify click coordinates (or use the current mouse position), so that I can target specific areas of the screen
18. As a power user, I want to pass `null` for coordinates in my scripts, so that actions use the current mouse position dynamically
19. As a user, I want the tool to loop scripts by default, so that I don't have to repeat sequences manually
20. As a power user, I want to stop a script from looping using the `once()` command, so that I can run a script exactly once
21. As a user, I want the tool to exit completely when I use the `exit()` command in a script, so that I can terminate the auto-clicker daemon from within a script
22. As a user, I want to set a custom window title for the tray app, so that I can identify which instance I'm controlling when running multiple profiles
23. As a user, I want the tool to work on both X11 and Wayland without configuration changes, so that I can switch desktop sessions without reconfiguring
24. As a sysadmin, I want to configure the auto-clicker via a YAML config file, so that I can version-control and distribute settings across machines
25. As a user, I want the config file to support comments, so that I can annotate my settings for future reference
26. As a user, I want to install MouseClicker via Flatpak or AppImage, so that I don't need to manage Python dependencies manually
27. As a user, I want the tool to automatically detect available input devices on my system, so that I don't need to manually specify `/dev/input/event*` paths
28. As a power user, I want the TrayApp to communicate with the Daemon via Unix socket IPC, so that they can coordinate start/stop/profile switching across separate processes
29. As a user, I want the auto-clicker to continue running as a background daemon even after I close the GUI, so that my scheduled tasks complete
30. As a user, I want to see the current status of the auto-clicker (running/stopped, active profile, next scheduled action) in the tray icon tooltip, so that I can monitor it at a glance
31. As a user, I want the tool to validate my YAML config on load and show clear error messages, so that I can fix typos and misconfigurations quickly
32. As a power user, I want to run the DSL parser and script engine as a separate module, so that I can test script parsing independently from the click engine
33. As a user, I want the tool to handle hotkey conflicts gracefully, so that pressing my toggle hotkey doesn't trigger unintended actions in other applications
34. As a user, I want the auto-clicker to inject events at the kernel level via evdev, so that it works with games and applications that ignore X11/XTest synthetic events
35. As a user, I want to configure the jitter range independently for position (pixels) and timing (milliseconds), so that I can fine-tune how "human-like" my clicks appear
36. As a power user, I want the CLI to support listing available profiles, so that I can manage them from the terminal
37. As a user, I want the tool to create a default config file if one doesn't exist, so that I can start using it immediately without manual setup
38. As a user, I want the script engine to execute commands sequentially with proper error handling, so that a failure in one command doesn't crash the entire script
39. As a user, I want to run scripts with elevated privileges (sudo) when needed, so that I can click on applications that require admin permissions
40. As a user, I want the tool to log its activity to a file, so that I can debug issues or audit what scripts have run

## Implementation Decisions

### Architecture

The system consists of three main components that communicate via IPC:

1. **Daemon** — The core engine that runs independently of the GUI. It:
   - Listens for Hotkey events via evdev
   - Executes ClickProfiles in a continuous loop
   - Parses and runs Scripts (`.msck` files)
   - Manages Schedule triggers (simple delay and cron)
   - Applies Jitter to each click action
   - Exposes a Unix socket for IPC commands from TrayApp and CLI

2. **TrayApp** — The PyQt6 system-tray GUI that:
   - Displays a tray icon with status indicator
   - Provides start/stop controls
   - Allows profile selection and creation
   - Configures jitter, interval, and hotkey settings
   - Loads and runs Scripts
   - Displays schedule information
   - Communicates with the Daemon via IPC

3. **CLI** — The command-line interface that:
   - Starts, stops, and checks the status of the Daemon
   - Manages ClickProfiles (list, create, edit, delete, set default)
   - Runs Scripts
   - Reads/writes Config

### Modules

| Module | Responsibility |
|--------|---------------|
| `ClickType` | Enum of mouse actions (left_click, right_click, long_press, scroll_up, scroll_down) + evdev injection |
| `ClickProfile` | Named configuration: ClickType, interval, coordinates, jitter, schedule |
| `Jitter` | Applies random position (±px) and timing (±ms) perturbation |
| `Schedule` | Manages simple delay and cron-based triggers |
| `Hotkey` | Listens for global keyboard shortcuts via evdev |
| `Script` | Parses `.msck` DSL files and executes commands |
| `Daemon` | Orchestrates all modules, manages the click loop, handles IPC |
| `TrayApp` | PyQt6 system-tray GUI for visual control |
| `CLI` | Terminal interface for Daemon management |
| `Config` | YAML config loader/saver |

### Interfaces

- **Daemon IPC** — Unix domain socket with commands: `start`, `stop`, `status`, `switch_profile`, `load_script`, `set_jitter`, `set_hotkey`
- **Config Schema** — YAML file at `~/.config/mouseclicker/config.yaml` with sections: `default_profile`, `hotkey`, `jitter`, `schedule`, `profiles`
- **Script DSL** — `.msck` files with commands: `delay`, `left_click`, `right_click`, `left_click_long`, `right_click_long`, `mouse_wheel`, `create_process`, `once`, `exit`, `title`

### Technical Clarifications

- evdev is used for both mouse event injection and hotkey listening (single backend)
- Scripts loop by default; `once()` stops looping
- `left_click_long` and `right_click_long` use type parameter: 1=press, 2=release
- Coordinates can be `null` in scripts to use current mouse position
- Cron expressions use standard 5-field format (minute, hour, day of month, month, day of week)
- The Daemon runs as a separate process from the TrayApp and CLI

### Architectural Decisions

- **ADR-001**: evdev over XTest — works on both X11 and Wayland, single backend
- **ADR-002**: PyQt6 over GTK — mature API, excellent tray support, dark mode via qdarkstyle
- **ADR-003**: .msck DSL over Python scripts — simple syntax, no Python knowledge required
- **ADR-004**: YAML over JSON/TOML — human-readable, supports comments

### Distribution

- Flatpak (primary) — `com.mouseclicker.MouseClicker`
- AppImage (secondary) — for distros without Flatpak support
- pip install (development) — for developers and advanced users
- systemd service (optional) — for headless/daemon mode

## Testing Decisions

### What makes a good test

- Test external behavior only (what the module does, not how it does it)
- Test the Daemon's click output by mocking evdev, not by clicking on screen
- Test the DSL parser by feeding input and checking parsed AST, not by running scripts
- Test the Config module by reading/writing YAML files and validating schema
- Test the TrayApp by verifying UI state changes, not by pixel comparison
- Test the Hotkey module by simulating evdev events, not by pressing real keys

### Modules to be tested

| Module | Test Type | Approach |
|--------|-----------|----------|
| `ClickType` | Unit | Mock evdev, verify correct event injection |
| `ClickProfile` | Unit | Create profiles, validate properties |
| `Jitter` | Unit | Verify jitter range, distribution |
| `Schedule` | Unit | Test cron parsing, delay calculation |
| `Hotkey` | Unit | Simulate evdev events, verify hotkey detection |
| `Script` | Unit + Integration | Parse DSL, verify AST; run scripts with mocked evdev |
| `Daemon` | Integration | Start daemon, send IPC commands, verify behavior |
| `TrayApp` | Integration | Verify UI state, tray icon, menu actions |
| `CLI` | Integration | Run CLI commands, verify output |
| `Config` | Unit | Load/save YAML, validate schema |

### Prior Art

- pytest for test framework
- pytest-qt for GUI testing
- pytest-asyncio for async Daemon tests
- Mock evdev device for click injection tests
- Temporary YAML files for config tests

## Out of Scope

- **Windows support** — This is Linux-only (evdev required)
- **macOS support** — No plans for macOS (would require Quartz API)
- **Cloud/remote control** — No web dashboard or mobile app
- **Multi-monitor support** — Coordinates are relative to the primary monitor
- **Click patterns** — No built-in patterns (circle, square, line); only coordinate-based
- **Image recognition** — No "click on this image" feature
- **Macro recording** — No GUI-based recording of mouse movements
- **Plugin system** — No extensible plugin architecture in v1
- **Network sync** — No cloud sync of profiles between machines

## Further Notes

### Dependencies

- `PyQt6>=6.6` — GUI framework
- `pyyaml>=6.0` — Config format
- `evdev>=1.7` — Linux input device access
- `croniter>=2.0` — Cron expression parsing
- `qdarkstyle>=3.2` — Dark mode for PyQt6

### Platform Requirements

- Linux kernel 4.14+ (for evdev support)
- Python 3.10+
- Read access to `/dev/input/event*` (may require `sudo` or udev rules)

### Future Considerations

- Multi-monitor coordinate mapping
- Click pattern generation (geometric shapes)
- Image-based click targeting
- Plugin system for custom commands
- Cross-desktop notification integration
- Web-based remote control dashboard
