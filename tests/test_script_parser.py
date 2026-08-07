import pytest
from src.mouseclicker.script.parser import DSLParser, DSLCommand


class TestDSLParser:
    """Tests for .msck DSL parser."""

    def test_parse_delay(self):
        """Should parse delay command."""
        parser = DSLParser()
        commands = parser.parse("delay(1000)")
        assert len(commands) == 1
        assert isinstance(commands[0], DSLCommand)
        assert commands[0].name == "delay"
        assert commands[0].args == [1000]

    def test_parse_left_click(self):
        """Should parse left_click command with coordinates."""
        parser = DSLParser()
        commands = parser.parse("left_click(300, 500)")
        assert len(commands) == 1
        assert commands[0].name == "left_click"
        assert commands[0].args == [300, 500]

    def test_parse_left_click_null_coords(self):
        """Should parse left_click with null coordinates."""
        parser = DSLParser()
        commands = parser.parse("left_click(null, null)")
        assert len(commands) == 1
        assert commands[0].name == "left_click"
        assert commands[0].args == [None, None]

    def test_parse_right_click(self):
        """Should parse right_click command."""
        parser = DSLParser()
        commands = parser.parse("right_click(100, 200)")
        assert len(commands) == 1
        assert commands[0].name == "right_click"
        assert commands[0].args == [100, 200]

    def test_parse_long_press(self):
        """Should parse left_click_long command."""
        parser = DSLParser()
        commands = parser.parse("left_click_long(300, 500, 1)")
        assert len(commands) == 1
        assert commands[0].name == "left_click_long"
        assert commands[0].args == [300, 500, 1]

    def test_parse_mouse_wheel(self):
        """Should parse mouse_wheel command."""
        parser = DSLParser()
        commands = parser.parse("mouse_wheel(400)")
        assert len(commands) == 1
        assert commands[0].name == "mouse_wheel"
        assert commands[0].args == [400]

    def test_parse_mouse_wheel_negative(self):
        """Should parse mouse_wheel with negative value."""
        parser = DSLParser()
        commands = parser.parse("mouse_wheel(-400)")
        assert len(commands) == 1
        assert commands[0].name == "mouse_wheel"
        assert commands[0].args == [-400]

    def test_parse_create_process(self):
        """Should parse create_process command."""
        parser = DSLParser()
        commands = parser.parse('create_process("/usr/bin/firefox")')
        assert len(commands) == 1
        assert commands[0].name == "create_process"
        assert commands[0].args == ["/usr/bin/firefox"]

    def test_parse_once(self):
        """Should parse once command."""
        parser = DSLParser()
        commands = parser.parse("once()")
        assert len(commands) == 1
        assert commands[0].name == "once"
        assert commands[0].args == []

    def test_parse_exit(self):
        """Should parse exit command."""
        parser = DSLParser()
        commands = parser.parse("exit()")
        assert len(commands) == 1
        assert commands[0].name == "exit"
        assert commands[0].args == []

    def test_parse_title(self):
        """Should parse title command."""
        parser = DSLParser()
        commands = parser.parse('title("My Script")')
        assert len(commands) == 1
        assert commands[0].name == "title"
        assert commands[0].args == ["My Script"]

    def test_parse_multiple_commands(self):
        """Should parse multiple commands from a script."""
        parser = DSLParser()
        script = """
delay(1000)
left_click(300, 500)
delay(500)
right_click(100, 200)
"""
        commands = parser.parse(script)
        assert len(commands) == 4

    def test_parse_ignores_comments(self):
        """Should ignore lines starting with #."""
        parser = DSLParser()
        script = """
# This is a comment
delay(1000)
# Another comment
left_click(100, 200)
"""
        commands = parser.parse(script)
        assert len(commands) == 2

    def test_parse_ignores_empty_lines(self):
        """Should ignore empty lines."""
        parser = DSLParser()
        script = """
delay(1000)

left_click(100, 200)

"""
        commands = parser.parse(script)
        assert len(commands) == 2

    def test_parse_case_insensitive(self):
        """Should handle case-insensitive commands."""
        parser = DSLParser()
        commands = parser.parse("DELAY(1000)")
        assert len(commands) == 1
        assert commands[0].name == "delay"

    def test_parse_invalid_command_raises(self):
        """Should raise ValueError for invalid commands."""
        parser = DSLParser()
        with pytest.raises(ValueError):
            parser.parse("invalid_command(100)")

    def test_parse_invalid_args_raises(self):
        """Should raise ValueError for invalid argument count."""
        parser = DSLParser()
        with pytest.raises(ValueError):
            parser.parse("delay()")

    def test_parse_from_file(self, tmp_path):
        """Should load and parse from file."""
        script_file = tmp_path / "test.msck"
        script_file.write_text("delay(1000)\nleft_click(100, 200)\n")
        parser = DSLParser()
        commands = parser.parse_file(str(script_file))
        assert len(commands) == 2

    def test_parse_right_click_long(self):
        """Should parse right_click_long command."""
        parser = DSLParser()
        commands = parser.parse("right_click_long(300, 500, 2)")
        assert len(commands) == 1
        assert commands[0].name == "right_click_long"
        assert commands[0].args == [300, 500, 2]
