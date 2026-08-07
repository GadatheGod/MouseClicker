"""Script execution engine for .msck DSL scripts."""

from __future__ import annotations

import subprocess
import time

from .parser import DSLCommand


class ScriptEngine:
    """Executes a sequence of DSL commands.

    Attributes:
        title: The current window title (set by title command).
    """

    def __init__(self) -> None:
        self.title: str = ""

    def run(self, commands: list[DSLCommand], loop: bool = True) -> str:
        """Run a list of DSL commands.

        Args:
            commands: List of DSLCommand objects to execute.
            loop: Whether to loop the commands indefinitely.

        Returns:
            One of: 'completed', 'stop', 'exit'
        """
        iteration = 0
        while True:
            stop_encountered = False
            for cmd in commands:
                result = self.execute(cmd)
                if result == "exit":
                    return "exit"
                if result == "stop":
                    stop_encountered = True
                    break  # End of iteration

            if stop_encountered:
                return "stop"

            if not loop or iteration >= 1:
                return "completed"
            iteration += 1

    def execute(self, command: DSLCommand) -> str:
        """Execute a single DSL command.

        Args:
            command: The DSLCommand to execute.

        Returns:
            'completed' for normal commands, 'stop' for once(), 'exit' for exit().

        Raises:
            ValueError: If the command name is unknown.
        """
        if command.name == "delay":
            self._execute_delay(command.args[0])
            return "completed"

        if command.name in ("left_click", "right_click"):
            self._inject_click(command.name, command.args[0], command.args[1], None, None)
            return "completed"

        if command.name in ("left_click_long", "right_click_long"):
            x, y, type_val = command.args[0], command.args[1], command.args[2]
            self._inject_click(command.name, x, y, None, None, type_val)
            return "completed"

        if command.name == "mouse_wheel":
            self._execute_mouse_wheel(command.args[0])
            return "completed"

        if command.name == "create_process":
            self._execute_create_process(command.args[0])
            return "completed"

        if command.name == "once":
            return "stop"

        if command.name == "exit":
            return "exit"

        if command.name == "title":
            self._execute_title(command.args[0])
            return "completed"

        raise ValueError(f"Unknown command: {command.name}")

    def _execute_delay(self, ms: int) -> None:
        """Execute delay command."""
        time.sleep(ms / 1000.0)

    def _inject_click(self, cmd_name: str, x: int | None, y: int | None, current_x: int | None, current_y: int | None, type_val: int = 0) -> None:
        """Inject a click event (overridable for testing)."""
        from src.mouseclicker.click_type import ClickType

        if cmd_name == "left_click":
            click_type = ClickType.LEFT_CLICK
        elif cmd_name == "right_click":
            click_type = ClickType.RIGHT_CLICK
        elif cmd_name == "left_click_long":
            click_type = ClickType.LONG_PRESS
        elif cmd_name == "right_click_long":
            click_type = ClickType.LONG_PRESS
        else:
            return

        click_type.inject("/dev/input/event0", x, y, current_x, current_y)

    def _execute_mouse_wheel(self, value: int) -> None:
        """Execute mouse wheel command via xdotool."""
        if value > 0:
            subprocess.run(["xdotool", "mousewheel", str(value)], check=False)
        else:
            subprocess.run(["xdotool", "mousewheel", str(abs(value))], check=False)

    def _execute_create_process(self, path: str) -> None:
        """Execute create_process command."""
        subprocess.Popen(path, shell=True)

    def _execute_title(self, text: str) -> None:
        """Execute title command."""
        self.title = text
