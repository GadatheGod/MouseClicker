"""CLI entry point for MouseClicker."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import Config
from .click_profile import ClickProfile
from .click_type import ClickType
from .daemon import Daemon
from .script.parser import DSLParser
from .script.engine import ScriptEngine


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="mouseclicker",
        description="A mouse auto-clicker for Linux",
    )
    subparsers = parser.add_subparsers(dest="command")

    # start command
    start_parser = subparsers.add_parser("start", help="Start the auto-clicker")
    start_parser.add_argument("--profile", "-p", help="Profile name to use")
    start_parser.add_argument("--interval", "-i", type=int, help="Click interval in ms")
    start_parser.add_argument("--type", "-t", choices=["left_click", "right_click", "long_press", "scroll_up", "scroll_down"], help="Click type")

    # stop command
    subparsers.add_parser("stop", help="Stop the auto-clicker")

    # status command
    subparsers.add_parser("status", help="Show auto-clicker status")

    # profiles command
    profiles_parser = subparsers.add_parser("profiles", help="Manage click profiles")
    profiles_sub = profiles_parser.add_subparsers(dest="action")
    profiles_sub.add_parser("list", help="List available profiles")
    profiles_set = profiles_sub.add_parser("set", help="Set default profile")
    profiles_set.add_argument("name", help="Profile name")
    profiles_add = profiles_sub.add_parser("add", help="Add a new profile")
    profiles_add.add_argument("name", help="Profile name")
    profiles_add.add_argument("--type", "-t", choices=["left_click", "right_click", "long_press", "scroll_up", "scroll_down"], help="Click type")
    profiles_add.add_argument("--interval", "-i", type=int, help="Click interval in ms")
    profiles_edit = profiles_sub.add_parser("edit", help="Edit an existing profile")
    profiles_edit.add_argument("name", help="Profile name")
    profiles_edit.add_argument("--type", "-t", choices=["left_click", "right_click", "long_press", "scroll_up", "scroll_down"], help="Click type")
    profiles_edit.add_argument("--interval", "-i", type=int, help="Click interval in ms")
    profiles_del = profiles_sub.add_parser("delete", help="Delete a profile")
    profiles_del.add_argument("name", help="Profile name to delete")

    # script command
    script_parser = subparsers.add_parser("script", help="Run a script")
    script_sub = script_parser.add_subparsers(dest="action")
    script_run = script_sub.add_parser("run", help="Run a script file")
    script_run.add_argument("file", help="Path to .msck script file")

    # schedule command
    schedule_parser = subparsers.add_parser("schedule", help="Manage schedule")
    schedule_sub = schedule_parser.add_subparsers(dest="action")
    schedule_set = schedule_sub.add_parser("set", help="Set schedule")
    schedule_set.add_argument("--mode", "-m", choices=["delay", "cron"], help="Schedule mode")
    schedule_set.add_argument("--cron", "-c", help="Cron expression")
    schedule_set.add_argument("--delay", "-d", type=int, help="Delay in seconds")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    config = Config.load()

    if args.command == "start":
        cmd_start(args, config)
    elif args.command == "stop":
        cmd_stop()
    elif args.command == "status":
        cmd_status()
    elif args.command == "profiles":
        cmd_profiles(args, config)
    elif args.command == "script":
        cmd_script(args)
    elif args.command == "schedule":
        cmd_schedule(args, config)


def cmd_start(args: argparse.Namespace, config: Config) -> None:
    """Handle start command."""
    profile_name = args.profile or config.default_profile
    profile = config.get_profile(profile_name)

    if not profile:
        print(f"Profile '{profile_name}' not found. Available profiles: {list(config.profiles.keys())}")
        sys.exit(1)

    # Override with CLI args if provided
    if args.interval:
        profile.interval = args.interval
    if args.type:
        profile.click_type = ClickType(args.type)

    daemon = Daemon()
    daemon.start(profile)
    print(f"Auto-clicker started with profile: {profile.name}")


def cmd_stop() -> None:
    """Handle stop command."""
    daemon = Daemon()
    daemon.stop()
    print("Auto-clicker stopped")


def cmd_status() -> None:
    """Handle status command."""
    daemon = Daemon()
    status = daemon.get_status()
    if status["running"]:
        print(f"Status: Running (profile: {status['profile']})")
    else:
        print("Status: Stopped")


def cmd_profiles(args: argparse.Namespace, config: Config) -> None:
    """Handle profiles command."""
    if args.action == "list":
        if not config.profiles:
            print("No profiles configured.")
            return
        for name, profile in config.profiles.items():
            enabled = "enabled" if profile.enabled else "disabled"
            print(f"  {name}: {profile.click_type.value} @ {profile.interval}ms [{enabled}]")

    elif args.action == "set":
        config.default_profile = args.name
        config.save()
        print(f"Default profile set to: {args.name}")

    elif args.action == "add":
        click_type = ClickType(args.type) if args.type else ClickType.LEFT_CLICK
        interval = args.interval or 100
        profile = ClickProfile(name=args.name, click_type=click_type, interval=interval)
        config.add_profile(profile)
        config.save()
        print(f"Profile '{args.name}' created")

    elif args.action == "edit":
        profile = config.get_profile(args.name)
        if not profile:
            print(f"Profile '{args.name}' not found")
            sys.exit(1)
        if args.type:
            profile.click_type = ClickType(args.type)
        if args.interval:
            profile.interval = args.interval
        config.save()
        print(f"Profile '{args.name}' updated")

    elif args.action == "delete":
        if args.name in config.profiles:
            config.remove_profile(args.name)
            if config.default_profile == args.name:
                config.default_profile = next(iter(config.profiles), "default")
            config.save()
            print(f"Profile '{args.name}' deleted")
        else:
            print(f"Profile '{args.name}' not found")


def cmd_script(args: argparse.Namespace) -> None:
    """Handle script command."""
    script_path = Path(args.file)
    if not script_path.exists():
        print(f"Script not found: {args.file}")
        sys.exit(1)

    parser = DSLParser()
    commands = parser.parse_file(str(script_path))
    engine = ScriptEngine()
    result = engine.run(commands, loop=True)
    print(f"Script completed with result: {result}")


def cmd_schedule(args: argparse.Namespace, config: Config) -> None:
    """Handle schedule command."""
    if args.action == "set":
        if args.mode:
            config.schedule_mode = args.mode
        if args.cron:
            config.cron_expression = args.cron
        if args.delay is not None:
            config.delay_seconds = args.delay
        config.save()
        print("Schedule updated")


if __name__ == "__main__":
    main()
