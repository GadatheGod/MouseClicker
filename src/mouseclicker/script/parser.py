"""DSL parser for .msck script files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class DSLCommand:
    """Represents a parsed DSL command.

    Attributes:
        name: The command name (e.g. 'delay', 'left_click').
        args: List of parsed arguments.
    """

    name: str
    args: list[Any]


class DSLParser:
    """Parses .msck script files into a list of DSLCommand objects.

    Commands are case-insensitive, one per line.
    Comments start with #. Empty lines are ignored.
    """

    VALID_COMMANDS = {
        "delay",
        "left_click",
        "right_click",
        "left_click_long",
        "right_click_long",
        "mouse_wheel",
        "create_process",
        "once",
        "exit",
        "title",
    }

    # Regex to match command(name) or command(name, name2) patterns
    _COMMAND_RE = re.compile(r"^(\w+)\((.*)\)$", re.IGNORECASE)

    def parse(self, text: str) -> list[DSLCommand]:
        """Parse DSL text into a list of commands.

        Args:
            text: The DSL script text.

        Returns:
            List of parsed DSLCommand objects.

        Raises:
            ValueError: If an unknown command or invalid argument is found.
        """
        commands: list[DSLCommand] = []
        for line in text.splitlines():
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            command = self._parse_line(line)
            commands.append(command)
        return commands

    def parse_file(self, filepath: str) -> list[DSLCommand]:
        """Parse a .msck script file.

        Args:
            filepath: Path to the script file.

        Returns:
            List of parsed DSLCommand objects.
        """
        with open(filepath, "r") as f:
            return self.parse(f.read())

    def _parse_line(self, line: str) -> DSLCommand:
        """Parse a single DSL line."""
        match = self._COMMAND_RE.match(line)
        if not match:
            raise ValueError(f"Invalid DSL line: {line}")

        name = match.group(1).lower()
        args_str = match.group(2).strip()

        if name not in self.VALID_COMMANDS:
            raise ValueError(f"Unknown command: {name}")

        args = self._parse_args(name, args_str)
        return DSLCommand(name=name, args=args)

    def _parse_args(self, name: str, args_str: str) -> list[Any]:
        """Parse command arguments."""
        if name in ("once", "exit"):
            return []

        if name == "delay":
            return [self._parse_int(args_str, "delay")]

        if name == "mouse_wheel":
            return [self._parse_int(args_str, "mouse_wheel")]

        if name == "title":
            return [self._parse_string(args_str, "title")]

        if name == "create_process":
            return [self._parse_string(args_str, "create_process")]

        if name in ("left_click_long", "right_click_long"):
            parts = self._split_args(args_str)
            if len(parts) != 3:
                raise ValueError(f"{name} requires exactly 3 arguments")
            return [self._parse_coord(parts[0]), self._parse_coord(parts[1]), self._parse_int(parts[2], name)]

        # left_click, right_click
        parts = self._split_args(args_str)
        if len(parts) != 2:
            raise ValueError(f"{name} requires exactly 2 arguments")
        return [self._parse_coord(parts[0]), self._parse_coord(parts[1])]

    def _split_args(self, args_str: str) -> list[str]:
        """Split arguments by comma, respecting quotes."""
        parts: list[str] = []
        current = ""
        in_quote = False
        for char in args_str:
            if char == '"':
                in_quote = not in_quote
            elif char == "," and not in_quote:
                parts.append(current.strip())
                current = ""
            else:
                current += char
        if current.strip():
            parts.append(current.strip())
        return parts

    def _parse_coord(self, s: str) -> int | None:
        """Parse a coordinate argument (int or null)."""
        if s.lower() == "null":
            return None
        return int(s)

    def _parse_int(self, s: str, cmd_name: str) -> int:
        """Parse an integer argument."""
        try:
            return int(s)
        except ValueError:
            raise ValueError(f"Invalid integer argument for {cmd_name}: {s}")

    def _parse_string(self, s: str, cmd_name: str) -> str:
        """Parse a string argument (with optional quotes)."""
        if s.startswith('"') and s.endswith('"'):
            return s[1:-1]
        if s.startswith("'") and s.endswith("'"):
            return s[1:-1]
        return s
