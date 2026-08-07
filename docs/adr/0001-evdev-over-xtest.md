# ADR-001: evdev over XTest

## Context

MouseClicker needs to inject mouse events on Linux. There are multiple approaches available: `evdev` (direct device access), `XTest` (X11 extension), or hybrid libraries like `pynput`.

## Decision

We chose `evdev` as the primary input injection method.

## Consequences

### Positive
- Works on both X11 and Wayland
- Direct device access is fast and reliable
- Single backend for both mouse clicks and hotkeys
- No dependency on X11 display server

### Negative
- Requires read access to `/dev/input/event*`
- May need root/sudo on some systems
- Device paths can vary between machines

### Mitigations
- Add udev rules for non-root access
- Auto-detect available input devices
- Document sudo requirement in README
