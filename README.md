# MouseClicker

A simple, lightweight mouse auto-clicker for Linux. Built with Python, evdev, and PyQt6.
<img width="422" height="432" alt="image" src="https://github.com/user-attachments/assets/ce1dafc7-e0da-43da-98b0-a4ba1f298abf" />

## Features

- **Multiple click types** — Left click, right click, long press, scroll wheel
- **Customizable interval** — Configurable click interval in milliseconds
- **Global hotkeys** — Toggle start/stop with customizable keyboard shortcuts
- **Scheduled triggers** — Simple delay or cron-based recurring schedules
- **Dark mode GUI** — System-tray application with PyQt6 and green icon
- **Random jitter** — Position and timing perturbation to avoid detection
- **Custom scripts** — Write automation scripts using the `.msck` DSL
- **Multiple profiles** — Save and switch between click configurations
- **Headless mode** — Run as a systemd service without GUI

## Profiles & Use Cases

MouseClicker ships with **12 pre-configured profiles** for different use cases:

| Profile | Click Type | Interval | Use Case |
|---------|-----------|----------|----------|
| **gaming** | left_click | 50ms | Fast clicking in games (MMORPGs, idle games) |
| **fast_click** | left_click | 80ms | Quick clicks for form submissions |
| **slow_click** | left_click | 500ms | Gentle clicking for sensitive applications |
| **scroll_up** | scroll_up | 200ms | Auto-scrolling up in web pages/documents |
| **scroll_down** | scroll_down | 200ms | Auto-scrolling down in web pages/documents |
| **right_click** | right_click | 100ms | Right-click automation (context menus) |
| **long_press_1s** | long_press | 100ms | Hold 1 second (drag-and-drop operations) |
| **long_press_3s** | long_press | 100ms | Hold 3 seconds (file operations, selection) |
| **data_entry** | left_click | 150ms | Data entry automation (moderate speed) |
| **form_fill** | left_click | 300ms | Form filling (deliberate clicking) |
| **rapid_scroll** | scroll_up | 50ms | Rapid scrolling for quick navigation |
| **double_click** | left_click | 100ms | Double-click simulation |

### Managing Profiles

**View all profiles:**
```bash
python3 -m src.mouseclicker.cli profiles list
```

**Add a new profile:**
```bash
python3 -m src.mouseclicker.cli profiles add my_profile --type left_click --interval 100
```

**Set default profile:**
```bash
python3 -m src.mouseclicker.cli profiles set default gaming
```

**Edit a profile:**
```bash
python3 -m src.mouseclicker.cli profiles edit gaming --interval 75
```

**Delete a profile:**
```bash
python3 -m src.mouseclicker.cli profiles delete old_profile
```

## Installation

### From source

```bash
git clone https://github.com/GadatheGod/MouseClicker.git
cd MouseClicker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### GUI (System Tray)

```bash
cd MouseClicker
QT_QPA_PLATFORM=xcb PYTHONPATH=/path/to/.venv/lib/python3.12/site-packages python3 -m src.tray_app.main_window
```

The GUI provides:
- Green clock icon in system tray
- Main window with Start/Stop buttons
- Profile dropdown to select click configuration
- Settings button for jitter, hotkey, and schedule configuration

### CLI

```bash
# Start the auto-clicker
python3 -m src.mouseclicker.cli start --profile gaming --interval 50

# Stop the auto-clicker
python3 -m src.mouseclicker.cli stop

# Check status
python3 -m src.mouseclicker.cli status

# List profiles
python3 -m src.mouseclicker.cli profiles list

# Set a profile as default
python3 -m src.mouseclicker.cli profiles set default gaming

# Load a script
python3 -m src.mouseclicker.cli script run scripts/demo.msck
```

### Daemon / Systemd Service

```bash
# Install the systemd service
sudo cp packaging/mouseclicker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mouseclicker
sudo systemctl start mouseclicker
```

## Configuration

Configuration is stored in `~/.config/mouseclicker/config.yaml`:

```yaml
default_profile: gaming
hotkey:
  toggle: "Ctrl+Alt+A"
jitter:
  position: 3  # ±3 pixels
  timing: 20   # ±20ms
schedule:
  mode: cron        # or "delay"
  cron: "0 9 * * *" # every day at 9am
  delay: 0          # seconds
profiles:
  gaming:
    name: gaming
    click_type: left_click
    interval: 50
    coordinates: null  # null = current position
    long_press_duration: 0
    enabled: true
```

## Custom Scripts

MouseClicker supports a custom scripting language using `.msck` files.

### Example Script

```msck
# Wait 1 second
delay(1000)

# Left click at coordinates (300, 500)
left_click(300, 500)

# Wait 1 second
delay(1000)

# Right click at current position
right_click(null, null)

# Long press for 3 seconds
left_click_long(300, 500, 1)
delay(3000)
left_click_long(300, 500, 0)

# Scroll up
mouse_wheel(400)

# Launch a program
create_process("/usr/bin/firefox")

# Stop looping
once()
```

### DSL Reference

| Command | Parameters | Description |
|---------|-----------|-------------|
| `delay(ms)` | `ms` | Wait N milliseconds |
| `left_click(x, y)` | `x, y` | Click left button at coordinates |
| `right_click(x, y)` | `x, y` | Click right button at coordinates |
| `left_click_long(x, y, type)` | `x, y, type` | Long press (type: 1=press, 2=release) |
| `right_click_long(x, y, type)` | `x, y, type` | Long press (type: 1=press, 2=release) |
| `mouse_wheel(value)` | `value` | Scroll (positive=up, negative=down) |
| `create_process(path)` | `path` | Launch external program |
| `once()` | _(none)_ | Stop looping after current iteration |
| `exit()` | _(none)_ | Terminate the auto-clicker daemon |
| `title(text)` | `text` | Set the tray app window title |

## Development

### Requirements

- Python 3.10+
- Linux (evdev required)
- PyQt6

### Setup

```bash
# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run the application
QT_QPA_PLATFORM=xcb PYTHONPATH=/path/to/.venv/lib/python3.12/site-packages python3 -m src.tray_app.main_window
```

### Project Structure

See `PLAN.md` for the full project structure and implementation phases.

## FAQ

**How do I stop the auto-clicker if it's clicking too fast?**
Press the configured hotkey (default: `Ctrl+Alt+A`) to toggle it off. If the hotkey doesn't work, use the tray icon or CLI command `python3 -m src.mouseclicker.cli stop`.

**Can I use this on Wayland?**
Yes. MouseClicker uses `evdev` which works on both X11 and Wayland.

**Where is my configuration stored?**
Configuration is stored in `~/.config/mouseclicker/config.yaml`.

**How do I run as root?**
Some applications require elevated privileges. Run with `sudo`:
```bash
sudo QT_QPA_PLATFORM=xcb PYTHONPATH=/path/to/.venv/lib/python3.12/site-packages python3 -m src.tray_app.main_window
```

Or add your user to the input group:
```bash
sudo usermod -aG input $USER
```
Then log out and log back in.

## License

MIT License

## Credits

Inspired by [MouseClickTool](https://github.com/lalakii/MouseClickTool) for Windows.
