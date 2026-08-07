import pytest
from unittest.mock import patch, MagicMock
from src.mouseclicker.script.engine import ScriptEngine
from src.mouseclicker.script.parser import DSLCommand


class TestScriptEngine:
    """Tests for script execution engine."""

    def test_execute_delay(self):
        """Should execute delay command."""
        engine = ScriptEngine()
        cmd = DSLCommand("delay", [100])
        result = engine.execute(cmd)
        assert result == "completed"

    def test_execute_left_click(self):
        """Should execute left_click command."""
        engine = ScriptEngine()
        cmd = DSLCommand("left_click", [100, 200])
        with patch.object(engine, "_inject_click") as mock_inject:
            result = engine.execute(cmd)
            mock_inject.assert_called_once_with("left_click", 100, 200, None, None)
            assert result == "completed"

    def test_execute_right_click(self):
        """Should execute right_click command."""
        engine = ScriptEngine()
        cmd = DSLCommand("right_click", [100, 200])
        with patch.object(engine, "_inject_click") as mock_inject:
            result = engine.execute(cmd)
            mock_inject.assert_called_once_with("right_click", 100, 200, None, None)
            assert result == "completed"

    def test_execute_left_click_long_press(self):
        """Should execute left_click_long with press."""
        engine = ScriptEngine()
        cmd = DSLCommand("left_click_long", [100, 200, 1])
        with patch.object(engine, "_inject_click") as mock_inject:
            result = engine.execute(cmd)
            mock_inject.assert_called_once_with("left_click_long", 100, 200, None, None, 1)
            assert result == "completed"

    def test_execute_left_click_long_release(self):
        """Should execute left_click_long with release."""
        engine = ScriptEngine()
        cmd = DSLCommand("left_click_long", [100, 200, 2])
        with patch.object(engine, "_inject_click") as mock_inject:
            result = engine.execute(cmd)
            mock_inject.assert_called_once_with("left_click_long", 100, 200, None, None, 2)
            assert result == "completed"

    def test_execute_mouse_wheel(self):
        """Should execute mouse_wheel command."""
        engine = ScriptEngine()
        cmd = DSLCommand("mouse_wheel", [400])
        with patch("subprocess.run") as mock_run:
            result = engine.execute(cmd)
            assert result == "completed"

    def test_execute_once_returns_stop(self):
        """Should return 'stop' for once command."""
        engine = ScriptEngine()
        cmd = DSLCommand("once", [])
        result = engine.execute(cmd)
        assert result == "stop"

    def test_execute_exit_returns_exit(self):
        """Should return 'exit' for exit command."""
        engine = ScriptEngine()
        cmd = DSLCommand("exit", [])
        result = engine.execute(cmd)
        assert result == "exit"

    def test_execute_title_sets_title(self):
        """Should set title for title command."""
        engine = ScriptEngine()
        cmd = DSLCommand("title", ["My Script"])
        result = engine.execute(cmd)
        assert engine.title == "My Script"
        assert result == "completed"

    def test_execute_create_process(self):
        """Should execute create_process command."""
        engine = ScriptEngine()
        cmd = DSLCommand("create_process", ["/usr/bin/firefox"])
        with patch("subprocess.Popen") as mock_popen:
            result = engine.execute(cmd)
            mock_popen.assert_called_once_with("/usr/bin/firefox", shell=True)
            assert result == "completed"

    def test_execute_sequence(self):
        """Should execute a sequence of commands."""
        engine = ScriptEngine()
        commands = [
            DSLCommand("delay", [10]),
            DSLCommand("left_click", [100, 200]),
            DSLCommand("once", []),
        ]
        with patch.object(engine, "_inject_click"):
            result = engine.run(commands, loop=True)
            assert result == "stop"

    def test_execute_unknown_command_raises(self):
        """Should raise ValueError for unknown commands."""
        engine = ScriptEngine()
        cmd = DSLCommand("unknown_cmd", [])
        with pytest.raises(ValueError):
            engine.execute(cmd)

    def test_run_loop_stops_on_once(self):
        """Should stop looping when once() is encountered."""
        engine = ScriptEngine()
        commands = [
            DSLCommand("delay", [10]),
            DSLCommand("once", []),
        ]
        with patch.object(engine, "_inject_click"):
            result = engine.run(commands, loop=True)
            assert result == "stop"

    def test_run_loop_runs_until_exit(self):
        """Should stop looping when exit() is encountered."""
        engine = ScriptEngine()
        commands = [
            DSLCommand("delay", [10]),
            DSLCommand("exit", []),
        ]
        with patch.object(engine, "_inject_click"):
            result = engine.run(commands, loop=True)
            assert result == "exit"

    def test_run_no_loop_runs_once(self):
        """Should run once when loop=False."""
        engine = ScriptEngine()
        commands = [
            DSLCommand("delay", [10]),
        ]
        with patch.object(engine, "_inject_click"):
            result = engine.run(commands, loop=False)
            assert result == "completed"
