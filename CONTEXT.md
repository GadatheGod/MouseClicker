# MouseClicker Domain Model

## Glossary

### AutoClicker
The core daemon that simulates mouse clicks at configurable intervals. Runs as a background process (systemd service or daemon mode) or under GUI control. Uses `evdev` to inject events into `/dev/input/event*`.

### ClickProfile
A named set of click settings: click type, interval (ms), hotkey, jitter range, coordinates, and optional schedule. Multiple profiles can be saved and switched between.

### ClickType
The kind of mouse action to perform. One of:
- `left_click` — single left button press/release
- `right_click` — single right button press/release
- `long_press` — press, hold for duration, release
- `scroll_up` — scroll wheel up
- `scroll_down` — scroll wheel down

### Script
A `.msck` file that defines a sequence of automated actions. Uses a custom DSL (see DSL Commands below). Scripts loop by default; `once()` stops looping.

### DSL (Domain Specific Language)
The custom scripting syntax for `.msck` files. Commands are case-insensitive, one per line. Comments start with `#`. Parameters can be `null` to use current position.

### DSL Commands
| Command | Parameters | Description |
|---------|-----------|-------------|
| `delay` | `ms` | Wait N milliseconds |
| `left_click` | `x, y` | Click left button at coordinates |
| `right_click` | `x, y` | Click right button at coordinates |
| `left_click_long` | `x, y, type` | Long press (type: 1=press, 2=release) |
| `right_click_long` | `x, y, type` | Long press (type: 1=press, 2=release) |
| `mouse_wheel` | `value` | Scroll (positive=up, negative=down) |
| `create_process` | `path` | Launch external program |
| `once` | _(none)_ | Stop looping after current iteration |
| `exit` | _(none)_ | Terminate the auto-clicker daemon |
| `title` | `text` | Set the tray app window title |

### Hotkey
A global keyboard shortcut (e.g., `Ctrl+Alt+A`) that toggles the auto-clicker start/stop state. Listened via `evdev` on `/dev/input/event*`.

### Jitter
Random perturbation applied to make clicks appear human-like. Two types:
- **Position jitter**: ±N pixels offset from target coordinates
- **Timing jitter**: ±N milliseconds offset from configured interval

### Schedule
A time-based trigger for the auto-clicker. Two modes:
- **Simple delay**: Start after N seconds/minutes
- **Cron expression**: Recurring schedule parsed by `croniter`

### Config
Persistent settings stored as a YAML file in `~/.config/mouseclicker/`. Contains default click profile, hotkey bindings, jitter ranges, and schedule settings.

### TrayApp
The PyQt6 system-tray GUI application. Provides visual control of the auto-clicker: start/stop, profile selection, jitter settings, script runner, and schedule viewer. Lives in the system tray.

### Daemon
The headless background process that executes click profiles and scripts. Communicates with TrayApp via a local IPC mechanism (Unix socket or D-Bus). Can be started as a systemd service.

### IPC (Inter-Process Communication)
The mechanism by which TrayApp communicates with the Daemon. Uses a Unix domain socket for command exchange (start, stop, switch profile, load script, etc.).

## Relationships

- A **ClickProfile** contains one **ClickType**, a **Hotkey**, **Jitter** settings, and an optional **Schedule**.
- A **Script** contains a sequence of **DSL Commands**.
- The **TrayApp** controls the **Daemon** via **IPC**.
- The **Daemon** listens for **Hotkey** events and executes **ClickProfiles** or **Scripts**.
