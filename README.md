# MouseClicker

A simple, lightweight mouse auto-clicker for Linux. Built with Python, evdev, and PyQt6.

## Features

- **Multiple click types** — Left click, right click, long press, scroll wheel
- **Customizable interval** — Configurable click interval in milliseconds
- **Global hotkeys** — Toggle start/stop with customizable keyboard shortcuts
- **Scheduled triggers** — Simple delay or cron-based recurring schedules
- **Dark mode GUI** — System-tray application with PyQt6
- **Random jitter** — Position and timing perturbation to avoid detection
- **Custom scripts** — Write automation scripts using the `.msck` DSL
- **Multiple profiles** — Save and switch between click configurations
- **Headless mode** — Run as a systemd service without GUI

## Installation

### Flatpak

```bash
flatpak install flathub com.mouseclicker.MouseClicker
flatpak run com.mouseclicker.MouseClicker
```

### AppImage

```bash
chmod +x MouseClicker-*.AppImage
./MouseClicker-*.AppImage
```

### From source

```bash
git clone https://github.com/yourusername/MouseClicker.git
cd MouseClicker
pip install -r requirements.txt
python -m mouseclicker
```

## Usage

### System Tray GUI

Run the application and a tray icon will appear in your system tray. Right-click the tray icon to:

- Start/Stop auto-clicking
- Switch between click profiles
- Configure click interval, jitter, and hotkeys
- Load and run automation scripts
- View schedule settings

### CLI

```bash
# Start the auto-clicker
mouseclicker start

# Stop the auto-clicker
mouseclicker stop

# Check status
mouseclicker status

# List profiles
mouseclicker profiles list

# Set a profile as default
mouseclicker profiles set default <profile_name>

# Load a script
mouseclicker script run <script.msck>
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
default_profile: default
hotkey:
  toggle: "Ctrl+Alt+A"
jitter:
  position: 3  # ±2 pixels
  timing: 20   # ±20ms
schedule:
  mode: cron        # or "delay"
  cron: "0 9 * * *" # every day at 9am
  delay: 0          # seconds
profiles:
  default:
    click_type: left_click
    interval: 100
    coordinates: null  # null = current position
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
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run the application
python -m mouseclicker
```

### Project Structure

See `PLAN.md` for the full project structure and implementation phases.

## FAQ

**How do I stop the auto-clicker if it's clicking too fast?**
Press the configured hotkey (default: `Ctrl+Alt+A`) to toggle it off. If the hotkey doesn't work, use the tray icon or CLI command `mouseclicker stop`.

**Can I use this on Wayland?**
Yes. MouseClicker uses `evdev` which works on both X11 and Wayland.

**Where is my configuration stored?**
Configuration is stored in `~/.config/mouseclicker/config.yaml`.

**How do I run as root?**
Some applications require elevated privileges. Run with `sudo` or use `polkit` for permission elevation.

## License

MIT License

## Credits

Inspired by [MouseClickTool](https://github.com/lalakii/MouseClickTool) for Windows.
