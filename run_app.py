#!/usr/bin/env python3
"""CLI to load apps.json, select an app, and run its command in the app directory."""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import questionary


def resolve_directory(raw: str) -> Path:
    if raw.startswith("~") and len(raw) > 1:
        env_var = raw[1:]
        resolved = os.environ.get(env_var)
        if resolved:
            return Path(resolved).resolve()
        fallback = os.environ.get(
            "DEVELOPMENT",
            str(Path.home() / "Documents" / "code_projects" / "development"),
        )
        return Path(fallback).resolve()
    if raw.startswith("$"):
        env_var = raw[1:]
        resolved = os.environ.get(env_var)
        if resolved:
            return Path(resolved).resolve()
        raw = raw[1:]
    return Path(os.path.expanduser(raw)).resolve()


def load_apps(apps_path: Path) -> list[dict]:
    with open(apps_path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("apps.json must contain a JSON array")
    for i, app in enumerate(data):
        if not isinstance(app, dict) or "name" not in app or "directory" not in app or "command" not in app:
            raise ValueError(f"App at index {i} must have 'name', 'directory', and 'command'")
    return data


def clear_screen() -> None:
    print("\033[2J\033[H", end="", flush=True)


_EXIT = object()


def prompt_selection(apps: list[dict]) -> Optional[dict]:
    choices = [
        questionary.Choice(title=app["name"], value=app) for app in apps
    ] + [questionary.Choice(title="Exit", value=_EXIT)]
    result = questionary.select("Select an app to run:", choices=choices).ask()
    return None if result is _EXIT else result


def main() -> int:
    apps_path = Path(__file__).resolve().parent / "apps.json"
    if not apps_path.exists():
        print(f"Error: apps.json not found at {apps_path}", file=sys.stderr)
        return 1

    apps = load_apps(apps_path)
    if not apps:
        print("No apps defined in apps.json.")
        return 0

    clear_screen()
    selected = prompt_selection(apps)
    if selected is None:
        return 0

    work_dir = resolve_directory(selected["directory"])
    if not work_dir.exists():
        print(f"Error: Directory does not exist: {work_dir}", file=sys.stderr)
        return 1

    raw_cmd = selected["command"]
    print(f"\nRunning: {raw_cmd}")
    print(f"Working directory: {work_dir}\n")

    script_path = Path(__file__).resolve().parent / "run_app.sh"
    result = subprocess.run(
        ["bash", str(script_path), str(work_dir), raw_cmd],
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
